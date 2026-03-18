#!/usr/bin/env python3
"""
commit.py — Entry point for the AI-powered git commit CLI

Usage:
  commit              # detect unstaged → ask to stage → suggest → commit
  commit --add        # git add . → suggest → commit
  commit --push       # git add . → suggest → commit → git push
  commit --dry-run    # show suggestion only, don't commit

Install (Linux):
  sudo cp commit.py /usr/local/bin/commit
  sudo chmod +x /usr/local/bin/commit

Optional free AI key (openrouter.ai):
  export GEMINI_API_KEY="sk-or-..."
"""

import os
import sys
import argparse

# Allow running from any directory by adding script's folder to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from git_utils    import is_git_repo, get_staged_info, stage_all, get_unstaged, run_commit, run_push
from ai_suggest   import ask_ai
from local_suggest import local_suggest
from ui           import with_spinner, prompt_user


def main():
    parser = argparse.ArgumentParser(
        description="Smart git commit with AI + local fallback"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show suggestion only, don't commit")
    parser.add_argument("--push", action="store_true",
                        help="git add . + commit + push")
    parser.add_argument("--add", action="store_true",
                        help="git add . then commit")
    args = parser.parse_args()

    # Guard: must be inside a git repo
    if not is_git_repo():
        print("❌  Not a git repository.")
        sys.exit(1)

    # Stage files
    if args.add or args.push:
        stage_all()
        print("  ✦ git add . done")
    else:
        unstaged, untracked = get_unstaged()
        if unstaged or untracked:
            print("  ✦ Unstaged changes found:")
            for f in (unstaged + "\n" + untracked).strip().split("\n"):
                if f:
                    print(f"    {f}")
            ans = input("\n  Stage all? (Y/n): ").strip().lower()
            if ans in ("", "y", "yes"):
                stage_all()
                print("  ✦ git add . done\n")

    # Analyse staged diff
    info = get_staged_info()
    if not info or not info.get("files"):
        print("⚠️  No staged changes.")
        sys.exit(1)

    # Print diff summary
    print()
    for line in info["stat"].strip().split("\n")[:7]:
        print(f"  \033[2m{line}\033[0m")

    # Generate suggestion: AI first, local fallback
    has_key    = bool(os.environ.get("GEMINI_API_KEY"))
    suggestion = ""

    if has_key:
        suggestion = with_spinner(lambda: ask_ai(info["patch"]), "AI generating")
        source     = "🤖 AI" if suggestion else None

        if not suggestion:
            suggestion = local_suggest(info)
            source     = "⚡ local"
    else:
        suggestion = local_suggest(info)
        source     = "⚡ local"

    print(f"\n  \033[36m💡 {source} suggestion — edit or press Enter to commit\033[0m")

    # Interactive prompt
    final = prompt_user(suggestion)
    if not final:
        print("⚠️  Empty message — cancelled.")
        sys.exit(1)

    # Dry run
    if args.dry_run:
        print(f'\n  [dry-run] would commit: "{final}"')
        sys.exit(0)

    # Commit
    print()
    code = run_commit(final)
    if code != 0:
        sys.exit(code)

    # Push
    if args.push:
        print()
        run_push()


if __name__ == "__main__":
    main()
