"""Receipts: everything a call (or email action) leaves behind.

Three artifact builders and one dispatcher:
  write_outcome_note()  — markdown note in vault/calls/
  build_invoice_pdf()   — PDF in receipts/out/
  build_ics()           — calendar entry in receipts/out/
  deliver()             — push all of it to your phone via Telegram;
                          falls back to printing local paths when
                          TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID are unset.
"""

import datetime as dt
import uuid
from pathlib import Path

import requests

from . import config, vault

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


# --------------------------------------------------------------- outcome note

def write_outcome_note(script: str, contact: str, transcript, fields: dict) -> Path:
    lines = [
        f"# Call: {script.replace('_', ' ')} — {contact}",
        "",
        f"- **Date:** {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- **Outcome:** {fields.get('outcome', 'unknown')}",
        f"- **Next step:** {fields.get('next_step', '—')}",
        "",
        "## Summary",
        fields.get("summary", "(none)"),
    ]
    details = fields.get("details")
    if details:
        lines += ["", "## Details"]
        lines += [f"- **{k}:** {v}" for k, v in details.items()]
    lines += ["", "## Transcript"]
    lines += [f"- **{who.upper()}:** {text}" for who, text in transcript]
    lines.append("")
    return vault.write_call_note(f"{script}-{contact}", "\n".join(lines))


# ---------------------------------------------------------------- invoice PDF

def build_invoice_pdf(invoice: dict) -> Path:
    from fpdf import FPDF

    config.RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    number = invoice.get("number", "INV-DRAFT")
    currency = invoice.get("currency", "AED")
    items = invoice.get("items", [])
    total = sum(i.get("qty", 1) * i.get("unit_price", 0) for i in items)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 12, "INVOICE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Invoice no: {number}", new_x="LMARGIN", new_y="NEXT")
    if invoice.get("issued"):
        pdf.cell(0, 7, f"Issued: {invoice['issued']}", new_x="LMARGIN", new_y="NEXT")
    if invoice.get("due_date"):
        pdf.cell(0, 7, f"Due: {invoice['due_date']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, f"From: {config.get('BUSINESS_NAME', 'Your Business')}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Bill to: {invoice.get('client', '')}", new_x="LMARGIN", new_y="NEXT")
    if invoice.get("client_address"):
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, invoice["client_address"], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(235, 235, 235)
    pdf.cell(110, 8, "Description", border=1, fill=True)
    pdf.cell(20, 8, "Qty", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Unit", border=1, fill=True, align="R")
    pdf.cell(30, 8, "Amount", border=1, fill=True, align="R",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    for item in items:
        qty = item.get("qty", 1)
        unit = item.get("unit_price", 0)
        pdf.cell(110, 8, str(item.get("description", "")), border=1)
        pdf.cell(20, 8, str(qty), border=1, align="C")
        pdf.cell(30, 8, f"{unit:,.2f}", border=1, align="R")
        pdf.cell(30, 8, f"{qty * unit:,.2f}", border=1, align="R",
                 new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(160, 8, f"Total ({currency})", border=1, align="R")
    pdf.cell(30, 8, f"{total:,.2f}", border=1, align="R",
             new_x="LMARGIN", new_y="NEXT")

    path = config.RECEIPTS_DIR / f"{vault.slugify(number)}.pdf"
    pdf.output(str(path))
    return path


# ------------------------------------------------------------- calendar entry

def build_ics(event: dict) -> Path:
    config.RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    start = dt.datetime.strptime(event["start"], "%Y-%m-%d %H:%M")
    end = start + dt.timedelta(minutes=int(event.get("duration_minutes", 60)))
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def esc(text: str) -> str:
        return str(text).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

    body = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//unified-brain//receipts//EN",
        "BEGIN:VEVENT",
        f"UID:{uuid.uuid4()}@unified-brain",
        f"DTSTAMP:{stamp}",
        f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
        f"SUMMARY:{esc(event.get('summary', 'Follow-up'))}",
        f"LOCATION:{esc(event.get('location', ''))}",
        f"DESCRIPTION:{esc(event.get('description', ''))}",
        "END:VEVENT",
        "END:VCALENDAR",
        "",
    ])
    name = f"{start.strftime('%Y-%m-%d')}-{vault.slugify(event.get('summary', 'event'))}.ics"
    path = config.RECEIPTS_DIR / name
    path.write_text(body)
    return path


# ------------------------------------------------------------------- delivery

def deliver(summary: str, files: list) -> bool:
    """Push the receipt bundle to Telegram; return True if it went out."""
    token = config.get("TELEGRAM_BOT_TOKEN")
    chat_id = config.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("\n[receipts] Telegram not configured (TELEGRAM_BOT_TOKEN / "
              "TELEGRAM_CHAT_ID) — receipts kept locally:")
        for f in files:
            print(f"  {f}")
        return False

    requests.post(
        TELEGRAM_API.format(token=token, method="sendMessage"),
        data={"chat_id": chat_id, "text": summary[:4096]},
        timeout=30,
    ).raise_for_status()
    for path in files:
        with open(path, "rb") as fh:
            requests.post(
                TELEGRAM_API.format(token=token, method="sendDocument"),
                data={"chat_id": chat_id},
                files={"document": (Path(path).name, fh)},
                timeout=60,
            ).raise_for_status()
    print(f"[receipts] delivered to Telegram chat {chat_id}: "
          f"summary + {len(files)} file(s)")
    return True
