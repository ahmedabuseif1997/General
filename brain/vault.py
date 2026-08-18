"""The notes half of the brain: a plain-markdown vault under vault/.

Conventions (also spelled out in CLAUDE.md):
  vault/inbox.md     — running action log, newest at the bottom
  vault/contacts.md  — people and businesses, one ## section each
  vault/calls/       — one outcome note per call
"""

import datetime as dt
import re

from . import config

CALLS_DIR = config.VAULT_DIR / "calls"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "note"


def log_action(line: str) -> None:
    """Append one timestamped line to vault/inbox.md."""
    inbox = config.VAULT_DIR / "inbox.md"
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    with inbox.open("a") as f:
        f.write(f"- {stamp} — {line}\n")


def write_call_note(title: str, body: str) -> "config.Path":
    CALLS_DIR.mkdir(parents=True, exist_ok=True)
    date = dt.date.today().isoformat()
    path = CALLS_DIR / f"{date}-{slugify(title)}.md"
    n = 2
    while path.exists():
        path = CALLS_DIR / f"{date}-{slugify(title)}-{n}.md"
        n += 1
    path.write_text(body)
    return path
