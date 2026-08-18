"""Telegram surface: the brain in your pocket.

Long-polls the Bot API; every incoming message goes through the brain
(headless Claude Code), the reply comes back as a message, and any new
files the brain dropped into receipts/out/ during the turn are attached
as documents.

Setup:
  1. @BotFather -> /newbot -> put the token in .env as TELEGRAM_BOT_TOKEN
  2. Message your bot once, run this, and it prints your chat id;
     put it in .env as TELEGRAM_CHAT_ID (also locks the bot to you).

Run:  python3 -m surfaces.telegram_bot
"""

import sys
import time
import traceback

import requests

from brain import config
from brain.claude_client import BrainUnavailable, run_brain

API = "https://api.telegram.org/bot{token}/{method}"


def call(token: str, method: str, **params):
    resp = requests.post(API.format(token=token, method=method),
                         data=params, timeout=90)
    resp.raise_for_status()
    return resp.json()["result"]


def send_text(token: str, chat_id: str, text: str) -> None:
    for i in range(0, len(text), 4096):
        call(token, "sendMessage", chat_id=chat_id, text=text[i:i + 4096])


def send_file(token: str, chat_id: str, path) -> None:
    with open(path, "rb") as fh:
        requests.post(API.format(token=token, method="sendDocument"),
                      data={"chat_id": chat_id},
                      files={"document": (path.name, fh)},
                      timeout=120).raise_for_status()


def snapshot_receipts() -> set:
    config.RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    return {p for p in config.RECEIPTS_DIR.iterdir() if p.is_file()}


def main() -> None:
    token = config.get("TELEGRAM_BOT_TOKEN")
    if not token:
        sys.exit("TELEGRAM_BOT_TOKEN not set in .env (get one from @BotFather)")
    allowed = config.get("TELEGRAM_CHAT_ID")
    print("telegram surface up — long-polling …")

    offset = 0
    while True:
        try:
            updates = call(token, "getUpdates", offset=offset, timeout=50)
        except requests.RequestException as exc:
            print(f"[telegram] poll error, retrying: {exc}")
            time.sleep(5)
            continue

        for update in updates:
            offset = update["update_id"] + 1
            msg = update.get("message") or {}
            chat_id = str(msg.get("chat", {}).get("id", ""))
            text = msg.get("text", "")
            if not chat_id or not text:
                continue
            if not allowed:
                print(f"[telegram] message from chat {chat_id} — set "
                      f"TELEGRAM_CHAT_ID={chat_id} in .env to enable it")
                continue
            if chat_id != allowed:
                print(f"[telegram] ignoring unknown chat {chat_id}")
                continue

            print(f"[telegram] <- {text}")
            before = snapshot_receipts()
            try:
                reply = run_brain(f"[surface: telegram] {text}") or "(no reply)"
            except BrainUnavailable as exc:
                reply = f"brain error: {exc}"
            except Exception:
                reply = "brain crashed:\n" + traceback.format_exc()[-1500:]
            send_text(token, chat_id, reply)
            for path in sorted(snapshot_receipts() - before):
                send_file(token, chat_id, path)
                print(f"[telegram] -> attached {path.name}")


if __name__ == "__main__":
    main()
