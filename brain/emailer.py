"""Email actions for the brain: send, reply, list.

Uses plain SMTP/IMAP with an app password (Gmail: create one at
https://myaccount.google.com/apppasswords) so it works from any surface,
headless. Configure EMAIL_ADDRESS and EMAIL_APP_PASSWORD in .env.

CLI (this is what the brain runs):
  python3 -m brain.emailer send  --to a@b.c --subject "Hi" --body "..." [--attach file.pdf]
  python3 -m brain.emailer list  [--query "from:someone"] [--n 10]
  python3 -m brain.emailer reply --id <imap-id> --body "..."
"""

import argparse
import email
import email.utils
import imaplib
import smtplib
import sys
from email.message import EmailMessage
from email.header import decode_header
from pathlib import Path

from . import config, vault


def _creds():
    addr = config.get("EMAIL_ADDRESS")
    pw = config.get("EMAIL_APP_PASSWORD")
    if not addr or not pw:
        sys.exit("EMAIL_ADDRESS / EMAIL_APP_PASSWORD not set in .env")
    return addr, pw


def _decode(value: str) -> str:
    parts = decode_header(value or "")
    return "".join(
        p.decode(enc or "utf-8", "replace") if isinstance(p, bytes) else p
        for p, enc in parts
    )


def _smtp_send(msg: EmailMessage) -> None:
    addr, pw = _creds()
    host = config.get("SMTP_HOST", "smtp.gmail.com")
    port = int(config.get("SMTP_PORT", "465"))
    with smtplib.SMTP_SSL(host, port) as smtp:
        smtp.login(addr, pw)
        smtp.send_message(msg)


def _imap():
    addr, pw = _creds()
    conn = imaplib.IMAP4_SSL(config.get("IMAP_HOST", "imap.gmail.com"))
    conn.login(addr, pw)
    conn.select("INBOX")
    return conn


def send(to: str, subject: str, body: str, attachments=()) -> None:
    addr, _ = _creds()
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = addr, to, subject
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg.set_content(body)
    for att in attachments:
        data = Path(att).read_bytes()
        maintype, subtype = ("application", "pdf") if att.endswith(".pdf") else ("application", "octet-stream")
        msg.add_attachment(data, maintype=maintype, subtype=subtype,
                           filename=Path(att).name)
    _smtp_send(msg)
    vault.log_action(f"emailed {to}: {subject}")
    print(f"sent to {to}: {subject}")


def list_inbox(query: str = "", n: int = 10) -> None:
    conn = _imap()
    criteria = f'(TEXT "{query}")' if query else "ALL"
    _, data = conn.search(None, criteria)
    ids = data[0].split()[-n:]
    for mid in reversed(ids):
        _, msgdata = conn.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
        hdr = email.message_from_bytes(msgdata[0][1])
        print(f"[{mid.decode()}] {_decode(hdr['From'])} — "
              f"{_decode(hdr['Subject'])} — {hdr['Date']}")
    conn.logout()


def reply(imap_id: str, body: str) -> None:
    addr, _ = _creds()
    conn = _imap()
    _, msgdata = conn.fetch(imap_id.encode(), "(RFC822)")
    original = email.message_from_bytes(msgdata[0][1])
    conn.logout()

    msg = EmailMessage()
    msg["From"] = addr
    msg["To"] = original.get("Reply-To") or original["From"]
    subject = _decode(original["Subject"] or "")
    msg["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    msg["In-Reply-To"] = original.get("Message-ID", "")
    msg["References"] = (original.get("References", "") + " "
                         + original.get("Message-ID", "")).strip()
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg.set_content(body)
    _smtp_send(msg)
    vault.log_action(f"replied to {msg['To']}: {msg['Subject']}")
    print(f"replied to {msg['To']}: {msg['Subject']}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="brain.emailer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("send")
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--attach", action="append", default=[])

    p = sub.add_parser("list")
    p.add_argument("--query", default="")
    p.add_argument("--n", type=int, default=10)

    p = sub.add_parser("reply")
    p.add_argument("--id", required=True, help="IMAP id from `list`")
    p.add_argument("--body", required=True)

    args = parser.parse_args()
    if args.cmd == "send":
        send(args.to, args.subject, args.body, args.attach)
    elif args.cmd == "list":
        list_inbox(args.query, args.n)
    elif args.cmd == "reply":
        reply(args.id, args.body)


if __name__ == "__main__":
    main()
