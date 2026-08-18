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
  phone/          PhoneAdapter interface; ships a keyboard-driven stub
                  plus a real Twilio Programmable Voice adapter
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

### Running the Telegram bot persistently

A long-polling bot needs to stay running to be useful — templates for
both are in `deploy/`:

**Linux (systemd user service)**
```bash
which claude   # note the directory — you may need it below
cp deploy/systemd/unified-brain-telegram.service ~/.config/systemd/user/
# edit the copied file: add claude's directory to the PATH= line if it's
# not already covered, and fix WorkingDirectory if the repo isn't ~/General
systemctl --user daemon-reload
systemctl --user enable --now unified-brain-telegram.service
loginctl enable-linger "$USER"   # keeps it running after you log out
journalctl --user -u unified-brain-telegram -f   # tail logs
```

**macOS (launchd)**
```bash
which python3   # and which claude
cp deploy/launchd/com.unifiedbrain.telegram.plist ~/Library/LaunchAgents/
# edit the copied file: fill in your username/repo path and python3 path
launchctl load ~/Library/LaunchAgents/com.unifiedbrain.telegram.plist
tail -f ~/General/telegram_bot.log
```

Both templates have `# EDIT` comments marking what to fill in for your
machine before installing.

## Placing an outbound call

```bash
python3 -m calls.runner invoice_chase \
  --contact "Ahmed" --number "+971500000000" \
  --context "invoice INV-1042, AED 1,200, 30 days overdue"
```

By default `PHONE_ADAPTER=stub` — you play the other side of the call at
the keyboard, so the whole pipeline (dialogue -> outcome extraction ->
receipts) runs with no telephony account.

### Going live with a real phone line (Twilio)

Set `PHONE_ADAPTER=twilio` in `.env` and fill in:

```
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+1...          # a Twilio number with voice enabled
TWILIO_WEBHOOK_BASE_URL=https://...   # see below
TWILIO_WEBHOOK_PORT=8080
```

Twilio drives the call by making HTTP requests back into a small
webhook server (`surfaces/phone/twilio_server.py`) that `calls/runner.py`
starts automatically. That server has to be reachable from the public
internet, so tunnel it — easiest with ngrok:

```bash
ngrok http 8080
```

Paste the `https://...ngrok...` URL ngrok prints into
`TWILIO_WEBHOOK_BASE_URL` (no trailing slash), then run
`calls/runner.py` as usual — it now places a real call. It uses Twilio's
built-in text-to-speech (`<Say>`) and speech recognition
(`<Gather input="speech">`), so no separate STT/TTS service is needed.
Webhook requests are verified against `X-Twilio-Signature` using your
auth token, so only Twilio can drive the call once the URL is public.

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
