"""The brain is a headless Claude Code invocation running in the repo root.

Every surface (desk mic, Telegram, phone) funnels text through run_brain().
Running in the repo root means CLAUDE.md (the brain's standing instructions)
and the vault are always in scope, whichever surface the request came from.

Override the command with BRAIN_CMD in .env, e.g. to pin a model or add
--permission-mode. The prompt is passed as the final argument.
"""

import os
import shlex
import subprocess

from . import config

DEFAULT_CMD = "claude -p --output-format text"


class BrainUnavailable(RuntimeError):
    pass


def run_brain(prompt: str, timeout: int = 600) -> str:
    argv = shlex.split(config.get("BRAIN_CMD", DEFAULT_CMD))
    try:
        proc = subprocess.run(
            argv + [prompt],
            cwd=config.REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
    except FileNotFoundError as exc:
        raise BrainUnavailable(
            f"brain command not found: {argv[0]!r}. Install Claude Code "
            "(https://claude.com/claude-code) or set BRAIN_CMD in .env"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise BrainUnavailable(f"brain timed out after {timeout}s") from exc
    if proc.returncode != 0:
        raise BrainUnavailable(
            f"brain exited {proc.returncode}: {proc.stderr.strip()[:500]}"
        )
    return proc.stdout.strip()
