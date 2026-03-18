"""
ai_suggest.py — AI commit message via Google Gemini (free tier)
No credit card needed. Get key at: https://aistudio.google.com/apikey

  export GEMINI_API_KEY="AIza..."

Free tier limits: 15 req/min, 1500 req/day on gemini-2.5-flash
"""

import os
import json
import urllib.request
import urllib.error

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Best free Gemini models — tried in order
FREE_MODELS = [
    "gemini-2.5-flash",       # best quality, free tier
    "gemini-2.5-flash-lite",  # faster, lighter fallback
]

SYSTEM_MSG = (
    "You are a git commit message expert. "
    "Analyze the diff and write ONE complete commit message. "
    "Format: type(scope): description. "
    "Types: feat, fix, refactor, chore, docs, style, test, perf. "
    "scope = main module changed. description = max 60 chars. "
    "Output ONLY the commit message. Nothing else. No quotes."
)


def ask_ai(diff: str) -> str:
    """
    Try Gemini free models one by one.
    Returns a commit message string, or '' if all models fail.
    Never raises — all errors caught silently.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return ""

    for model in FREE_MODELS:
        payload = json.dumps({
            "system_instruction": {
                "parts": [{"text": SYSTEM_MSG}]
            },
            "contents": [
                {"parts": [{"text": f"Diff:\n{diff}"}]}
            ],
            "generationConfig": {
                "maxOutputTokens": 80,
                "temperature": 0.1,
            }
        }).encode("utf-8")

        url = f"{GEMINI_BASE}/{model}:generateContent"
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "x-goog-api-key": api_key,
                "content-type":   "application/json",
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                raw  = data["candidates"][0]["content"]["parts"][0]["text"]
                if not raw:
                    continue
                msg = raw.strip().split("\n")[0].strip().strip('"').strip("'")
                if len(msg) >= 10 and ":" in msg:
                    return msg
        except urllib.error.HTTPError as e:
            if e.code in (429, 503, 404):
                continue   # rate limit or model unavailable — try next
            continue
        except Exception:
            continue       # timeout, parse error — try next silently

    return ""  # all models failed → caller uses local engine
