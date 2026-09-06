"""LifeOS morning open.

Opens lifeos.html in the default browser so the morning deck (today's learning
card + today's move) is simply waiting when you sit down. No toast, no email,
no notification: anything that can be blocked out will be blocked out. The tab
being there is the whole mechanism.

Schedule it for the time you sit down at the computer. See README.md for the
Task Scheduler (Windows), launchd (macOS) and cron (Linux) one-liners.

Run manually any time:  python scripts/morning_open.py
"""
import os
import subprocess
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parent / "lifeos.html"


def open_in_browser(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # noqa: S606 - opening a local file with its default handler
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


if __name__ == "__main__":
    open_in_browser(APP)
