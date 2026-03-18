"""
local_suggest.py — Offline Conventional Commits suggestion engine
No API, no internet, no rate limits. Works forever.
"""

import os
import re
from collections import defaultdict


# ── File path → commit type ───────────────────────────────────
TYPE_RULES = [
    (r"test[s]?[/\\]|_test\.|\.test\.|\.spec\.|test_|__tests__",   "test"),
    (r"readme|changelog|\.md$|docs?[/\\]|\.rst$|contributing",     "docs"),
    (r"\.css$|\.scss$|\.sass$|\.less$|\.styl$",                    "style"),
    (r"migration|migrate|alembic|\.sql$|seed\.",                    "chore"),
    (r"dockerfile|docker-compose|\.github[/\\]|ci\.yml|\.gitlab",  "chore"),
    (r"package\.json|requirements.*\.txt|pipfile|gemfile|cargo",   "chore"),
    (r"\.env|config[/\\]|settings\.|\.ini$|\.toml$|\.yaml$",      "chore"),
    (r"\.lock$|yarn\.lock|package-lock|poetry\.lock",              "chore"),
    (r"setup\.py|setup\.cfg|pyproject\.toml|manifest",            "chore"),
]

# ── File path → scope name ────────────────────────────────────
SCOPE_RULES = [

    # ── Auth & Security ───────────────────────────────────────
    (r"auth|login|logout|signin|signup|register",          "auth"),
    (r"token|jwt|oauth|session|cookie|credential",         "auth"),
    (r"password|passwd|hash|encrypt|decrypt|crypto",       "auth"),
    (r"permission|role|access|policy|guard|middleware",    "permissions"),
    (r"firewall|cors|csrf|xss|sanitize",                   "security"),

    # ── User & Profile ────────────────────────────────────────
    (r"user[s]?[/\\.]|account|profile|member|avatar",     "user"),
    (r"contact|address|phone|email",                       "user"),

    # ── Content / Domain models ───────────────────────────────
    (r"notice|announcement|bulletin|news",                 "notices"),
    (r"post[s]?[/\\.]|article|blog|content",               "posts"),
    (r"comment[s]?[/\\.]|review|rating|feedback",         "comments"),
    (r"product[s]?[/\\.]|item|catalog|inventory",         "products"),
    (r"order[s]?[/\\.]|cart|checkout|basket",             "orders"),
    (r"payment|invoice|billing|transaction|wallet",        "payments"),
    (r"category|tag|label|genre|topic",                    "category"),
    (r"search|filter|query|elastic|algolia",               "search"),
    (r"report|analytic|metric|stat|insight",               "analytics"),
    (r"notification|push|alert|email.*send|sms",           "notifications"),
    (r"message|chat|inbox|conversation|thread",            "messaging"),
    (r"event|calendar|schedule|booking|reservation",       "events"),
    (r"upload|media|file|attachment|asset|storage",        "media"),
    (r"gallery|image|photo|video|thumbnail",               "media"),
    (r"feed|timeline|stream|activity",                     "feed"),
    (r"subscription|plan|tier|membership",                 "subscription"),
    (r"coupon|discount|promo|voucher",                     "promotions"),
    (r"shipping|delivery|logistics|tracking",              "shipping"),

    # ── Admin & Dashboard ─────────────────────────────────────
    (r"admin[s]?[/\\.]|dashboard|panel|backoffice",       "admin"),
    (r"cms|content.manage",                                "cms"),

    # ── API Layer ─────────────────────────────────────────────
    (r"view[s]?\.py|viewset|apiview",                      "views"),
    (r"endpoint|route[s]?[/\\.]|url[s]?\.py",             "urls"),
    (r"serializer|schema|marshal|transform",               "serializers"),
    (r"validator|validation|form[s]?[/\\.]",               "validators"),
    (r"middleware",                                        "middleware"),
    (r"interceptor|hook[s]?[/\\.]",                       "hooks"),
    (r"graphql|resolver|mutation|subscription\.ts",        "graphql"),
    (r"websocket|socket|ws[/\\.]",                         "websocket"),

    # ── Data layer ────────────────────────────────────────────
    (r"model[s]?[/\\.]|entity|table|schema\.py",          "models"),
    (r"repo|repository",                                   "repository"),
    (r"service[s]?[/\\.]",                                 "service"),
    (r"dao|manager|store[s]?[/\\.]",                       "store"),
    (r"migration|migrate",                                 "migrations"),
    (r"seed|fixture|factory",                              "fixtures"),
    (r"cache|redis|memcache",                              "cache"),
    (r"celery|task[s]?[/\\.]|worker|queue|job",           "tasks"),
    (r"signal[s]?[/\\.]|event.*handler|listener",         "signals"),

    # ── Frontend — React / Next ───────────────────────────────
    (r"component[s]?[/\\.]|\.tsx$|\.jsx$",                "components"),
    (r"page[s]?[/\\.]|layout[s]?[/\\.]|screen",           "pages"),
    (r"context|provider|reducer|slice|zustand|recoil",    "state"),
    (r"hook[s]?[/\\.]|use[A-Z]",                          "hooks"),
    (r"style[s]?[/\\.]|theme|token\.css|design",          "styles"),
    (r"icon[s]?|svg[s]?[/\\.]|asset[s]?[/\\.]",          "assets"),
    (r"i18n|locale|translation|lang",                     "i18n"),
    (r"router|navigation|nav[/\\.]",                       "router"),
    (r"modal|dialog|popup|drawer|toast",                   "ui"),
    (r"table|list|grid|card|badge|button|input|form",     "ui"),
    (r"chart|graph|plot|visualization",                    "charts"),
    (r"animation|motion|transition",                       "animations"),

    # ── Flutter / Mobile ──────────────────────────────────────
    (r"widget|screen|view\.dart",                          "widgets"),
    (r"bloc|cubit|provider\.dart|riverpod",               "state"),
    (r"repository\.dart|datasource",                      "repository"),
    (r"model\.dart|entity\.dart",                         "models"),
    (r"service\.dart|api\.dart",                          "service"),
    (r"l10n|arb|intl",                                    "i18n"),
    (r"firebase|fcm|crashlytics",                         "firebase"),
    (r"esewa|khalti|payment\.dart",                       "payments"),

    # ── Backend infra ─────────────────────────────────────────
    (r"config[s]?[/\\.]|setting[s]?[/\\.]|env",           "config"),
    (r"log[s]?[/\\.]|logger|logging",                     "logging"),
    (r"exception|error[s]?[/\\.]|handler",                "errors"),
    (r"health|ping|status|monitor",                       "health"),
    (r"deploy|infra|k8s|helm|terraform|ansible",          "infra"),
    (r"nginx|apache|gunicorn|uwsgi",                      "server"),
    (r"celery|beat|cron",                                 "scheduler"),
    (r"test|spec|__test",                                  "tests"),
    (r"util[s]?[/\\.]|helper[s]?[/\\.]|common|shared",   "utils"),
    (r"constant[s]?[/\\.]|enum[s]?[/\\.]|type[s]?[/\\.]","types"),
    (r"lib[/\\.]|core[/\\.]|base[/\\.]|abstract",        "core"),
    (r"plugin|extension|addon",                           "plugins"),
    (r"script[s]?[/\\.]|tool[s]?[/\\.]|bin[/\\.]",       "scripts"),
    (r"docs?[/\\.]|document",                             "docs"),
]


def detect_scope(files: list) -> str:
    """Pick the most relevant scope from changed file paths."""
    votes = defaultdict(int)
    for f in files:
        fl = f.lower()
        matched = False
        for pattern, scope in SCOPE_RULES:
            if re.search(pattern, fl):
                votes[scope] += 1
                matched = True
                break
        if not matched:
            # Fall back to the most meaningful folder name
            for part in f.replace("\\", "/").split("/")[:-1]:
                if part not in ("src", "app", "apps", "lib", ".", "", "pages",
                                "components", "features", "modules", "core"):
                    votes[part] += 1
                    break
    return max(votes, key=votes.get) if votes else ""


def detect_type(info: dict) -> str:
    """Detect commit type from file patterns and patch content."""
    votes = defaultdict(int)

    for f in info["files"]:
        for pattern, t in TYPE_RULES:
            if re.search(pattern, f.lower()):
                votes[t] += 2
                break

    patch = info.get("patch", "")
    if re.search(r"^\+.*(fix|bug|error|exception|traceback|crash)",
                 patch, re.I | re.M): votes["fix"]  += 1
    if re.search(r"^\+.*(cache|memo|lazy|optim|perf|speed)",
                 patch, re.I | re.M): votes["perf"] += 1
    if re.search(r"^\+.*console\.(log|error)|^\+.*print\(|^\+.*debugger",
                 patch, re.M):        votes["chore"] += 1

    if votes and max(votes.values()) >= 2:
        return max(votes, key=votes.get)

    # Heuristic from change counts
    ins, dels = info["insertions"], info["deletions"]
    added     = info["added"]
    modified  = info["modified"]
    deleted   = info["deleted"]
    total     = len(info["files"])

    if len(deleted) == total:              return "chore"
    if len(added)   == total and ins > 0:  return "feat"
    if ins > 0 and dels > 0:
        if dels > ins * 1.5:               return "refactor"
        return "feat" if len(added) >= len(modified) else "refactor"
    return "chore"


def build_desc(info: dict, ctype: str, scope: str) -> str:
    """Build a human-readable description from the diff."""
    files   = info["files"]
    patch   = info.get("patch", "")
    added   = info["added"]
    deleted = info["deleted"]
    renamed = info["renamed"]

    # Extract new symbol names from patch
    syms = [
        s for s in re.findall(
            r"^\+\s*(?:def|class|function|const|async function|fn|func)\s+(\w+)",
            patch, re.M
        )
        if len(s) > 3 and not s.startswith("__")
    ][:3]

    if len(files) == 1:
        name = os.path.basename(files[0]).rsplit(".", 1)[0].replace("_", " ")
        if info["is_empty"]:                            return f"add empty {name} file"
        if deleted:                                     return f"remove {name}"
        if renamed:                                     return f"rename {name}"
        if syms:                                        return f"add {', '.join(syms)}"
        if added:                                       return f"add {name} module"
        if info["deletions"] > info["insertions"] * 2: return f"clean up {name}"
        return f"update {name}"

    if info["is_empty"]:
        names = ", ".join(os.path.basename(f).rsplit(".", 1)[0] for f in files[:3])
        return f"add empty {names} files"
    if len(deleted) == len(files): return f"remove {len(deleted)} files"
    if len(renamed) == len(files): return f"reorganize {scope or 'files'} structure"
    if syms and ctype in ("feat", "refactor"):
        return f"implement {', '.join(syms)}"
    if added and modified:
        return (f"restructure {scope} into feature module"
                if scope else f"restructure {len(files)} files")
    if ctype == "refactor": return f"refactor {scope or str(len(files)) + ' files'}"
    if ctype == "feat":     return f"implement {scope or 'new feature'}"
    return f"update {scope or str(len(files)) + ' files'}"


def local_suggest(info: dict) -> str:
    """Generate a Conventional Commit message. Returns '' if nothing staged."""
    if not info or not info.get("files"):
        return ""
    ctype = detect_type(info)
    scope = detect_scope(info["files"])
    desc  = build_desc(info, ctype, scope)
    msg   = f"{ctype}({scope}): {desc}" if scope else f"{ctype}: {desc}"
    return msg[:72]
