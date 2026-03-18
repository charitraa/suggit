"""
ui.py — Terminal UI components
Spinner for async operations + interactive prompt with pre-filled suggestion.
"""

import sys
import threading

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.styles import Style
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.key_binding import KeyBindings
except ImportError:
    print("❌  Run: pip install prompt_toolkit --break-system-packages")
    sys.exit(1)


def with_spinner(fn, msg: str = "Thinking") -> any:
    """
    Run fn() in a background thread and show a spinner while waiting.
    Returns the result of fn().
    """
    result = {"v": None}
    done   = threading.Event()

    def run():
        result["v"] = fn()
        done.set()

    threading.Thread(target=run, daemon=True).start()

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not done.wait(timeout=0.1):
        print(f"\r  {frames[i % len(frames)]}  {msg}...", end="", flush=True)
        i += 1

    print("\r" + " " * 40 + "\r", end="", flush=True)  # clear spinner
    return result["v"]


def prompt_user(suggestion: str) -> str:
    """
    Show an interactive prompt pre-filled with the suggestion.
      Enter    → accept and commit
      Edit     → modify freely with arrow keys / backspace
      Ctrl+A   → clear entire input
      Ctrl+C   → abort
    """
    kb = KeyBindings()

    @kb.add("c-a")
    def _(event):
        event.app.current_buffer.reset()

    try:
        return prompt(
            [("class:prompt", "  ✦ commit msg › ")],
            default=suggestion,
            style=Style.from_dict({"prompt": "bold ansigreen"}),
            bottom_toolbar=HTML(
                " <b>Enter</b> commit   "
                "<b>Ctrl+A</b> clear   "
                "<b>Ctrl+C</b> cancel"
            ),
            key_bindings=kb,
        ).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nAborted.")
        sys.exit(0)
