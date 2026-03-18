"""
git_utils.py — Git interaction helpers
Handles staging, diff parsing, commit and push.
"""

import re
import subprocess


def is_git_repo() -> bool:
    try:
        subprocess.check_output(
            ["git", "rev-parse", "--is-inside-work-tree"],
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_staged_info() -> dict:
    """Return structured info about staged changes."""
    try:
        stat        = subprocess.check_output(["git", "diff", "--staged", "--stat"],        stderr=subprocess.DEVNULL).decode().strip()
        name_status = subprocess.check_output(["git", "diff", "--staged", "--name-status"], stderr=subprocess.DEVNULL).decode().strip()
        patch       = subprocess.check_output(["git", "diff", "--staged"],                  stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        return {}

    added, modified, deleted, renamed, files = [], [], [], [], []
    for line in name_status.splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        s, fname = parts[0][0], parts[-1]
        files.append(fname)
        if   s == "A": added.append(fname)
        elif s == "M": modified.append(fname)
        elif s == "D": deleted.append(fname)
        elif s == "R": renamed.append(fname)

    ins  = sum(int(m.group(1)) for m in re.finditer(r"(\d+) insertion", stat))
    dels = sum(int(m.group(1)) for m in re.finditer(r"(\d+) deletion",  stat))

    return dict(
        files=files, added=added, modified=modified,
        deleted=deleted, renamed=renamed,
        insertions=ins, deletions=dels,
        patch=patch[:6000], stat=stat,
        is_empty=(ins == 0 and dels == 0)
    )


def stage_all():
    """Run git add ."""
    subprocess.run(["git", "add", "."])


def get_unstaged() -> tuple[str, str]:
    """Return (unstaged_files, untracked_files)."""
    unstaged  = subprocess.run(["git", "diff", "--name-only"],
                               capture_output=True, text=True).stdout.strip()
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                               capture_output=True, text=True).stdout.strip()
    return unstaged, untracked


def run_commit(msg: str) -> int:
    return subprocess.run(["git", "commit", "-m", msg]).returncode


def run_push():
    subprocess.run(["git", "push"])
