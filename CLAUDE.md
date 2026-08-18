# unified-brain

One brain (this Claude Code instance) behind three surfaces: a desk mic,
a Telegram bot, and a phone line. Same repo, same vault, same person on
the other end — you always have the full picture regardless of which
surface a request came in on.

## What you can do here

- **Notes**: `vault/` is a plain-markdown memory. Read it before acting on
  anything that references past context ("that invoice", "the garage
  guy"). Log actions to `vault/inbox.md` (append-only, newest at bottom).
  Keep people/businesses in `vault/contacts.md`.
- **Email**: `python3 -m brain.emailer send|list|reply ...` — see
  `brain/emailer.py` for flags. Requires `EMAIL_ADDRESS` /
  `EMAIL_APP_PASSWORD` in `.env`.
- **Outbound calls**: `python3 -m calls.runner <script> --contact "..." --number "..." --context "..."`
  Scripts: `invoice_chase`, `appointment_booking`, `price_inquiry`,
  `reservation` (defined in `calls/scripts/`). `PHONE_ADAPTER` in
  `.env` picks the line: `stub` (default) prompts at the keyboard for
  the other side's replies, so the whole pipeline can be exercised
  without a telephony account; `twilio` places real outbound calls via
  Twilio Programmable Voice (needs `TWILIO_ACCOUNT_SID` /
  `TWILIO_AUTH_TOKEN` / `TWILIO_FROM_NUMBER` / `TWILIO_WEBHOOK_BASE_URL`
  in `.env` — see README). Either way `calls/runner.py` and the scripts
  are unchanged.
- **Receipts**: every call produces an outcome note in `vault/calls/`,
  and — depending on the script — an invoice PDF and/or a `.ics`
  calendar entry in `receipts/out/`. `brain/receipts.py` pushes all of
  it to Telegram (`TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` in `.env`);
  without those set, it just prints the local file paths.

## Working conventions

- Keep replies short — this may be read on a phone screen or spoken
  aloud by the desk mic's TTS. No headers, no bullet walls, for
  conversational turns.
- When asked to do something that touches money, contacts, or a
  calendar, write it to the vault so the next surface picks it up.
- Don't invent phone numbers, emails, or invoice numbers — ask for them
  if they weren't given.
- This is a personal-automation pack for one user (see `userEmail` in
  system context for identity). Don't add multi-tenant/auth scaffolding
  — it's unnecessary here.

## Repo layout

```
brain/            core: config loader, vault I/O, receipts, emailer, the
                  headless-Claude-Code client every surface calls through
surfaces/         desk_mic.py, telegram_bot.py, phone/ (adapter + stub)
calls/            runner.py + scripts/ (the 4 outbound-call scripts)
vault/            your notes — inbox.md, contacts.md, calls/
receipts/out/     generated PDFs and .ics files (gitignored)
```
