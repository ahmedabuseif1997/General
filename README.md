# unified-brain

One brain (Claude Code + a plain-markdown vault) behind three surfaces —
a desk mic, Telegram, and a phone line — plus email actions and four
outbound-call scripts. Whatever surface you talk to it from, it's the
same brain with the same notes.

## Layout

```
brain/            core: config, vault I/O, receipts (PDF/.ics/Telegram
                  delivery), emailer, the headless-Claude-Code client
surfaces/
  desk_mic.py     push-to-talk voice loop (mic -> whisper -> brain -> TTS)
  telegram_bot.py long-polling Telegram bot, sends back replies + receipts
  phone/          PhoneAdapter interface; ships a keyboard-driven stub,
                  with a documented slot for a real line (Twilio etc.)
calls/
  runner.py       drives one call script end-to-end, writes receipts
  scripts/        invoice_chase, appointment_booking, price_inquiry,
                  reservation
vault/            inbox.md (action log), contacts.md, calls/ (outcomes)
receipts/out/     generated invoice PDFs and .ics files (gitignored)
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in what you need — see comments in the file
```

The brain itself is `claude` (Claude Code) run headlessly in this repo,
so it always has `CLAUDE.md` and `vault/` in scope. Any machine running
a surface needs the `claude` CLI installed and authenticated.

## Running a surface

```bash
python3 -m surfaces.telegram_bot     # Telegram bot
python3 -m surfaces.desk_mic         # push-to-talk voice loop
```

## Placing an outbound call

```bash
python3 -m calls.runner invoice_chase \
  --contact "Ahmed" --number "+971500000000" \
  --context "invoice INV-1042, AED 1,200, 30 days overdue"
```

By default `PHONE_ADAPTER=stub` — you play the other side of the call at
the keyboard, so the whole pipeline (dialogue -> outcome extraction ->
receipts) runs with no telephony account. Set `PHONE_ADAPTER=twilio`
once a real line is wired (see `surfaces/phone/twilio_adapter.py` for
the plan) — nothing else in the pack changes.

Every call produces an outcome note in `vault/calls/`, and — depending
on the script — an invoice PDF and/or calendar `.ics` in
`receipts/out/`. If `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` are set,
all of it is pushed straight to your phone; otherwise the local file
paths are printed.

## Email actions

```bash
python3 -m brain.emailer send  --to a@b.com --subject "Hi" --body "..." [--attach file.pdf]
python3 -m brain.emailer list  --query "from:someone" --n 10
python3 -m brain.emailer reply --id <imap-id> --body "..."
```

Requires `EMAIL_ADDRESS` / `EMAIL_APP_PASSWORD` (Gmail: create an app
password at https://myaccount.google.com/apppasswords) in `.env`.
