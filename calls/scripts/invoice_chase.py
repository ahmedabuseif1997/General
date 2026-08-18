"""Call a client about an unpaid invoice: confirm amount, get a payment date.

Receipts: outcome note + invoice PDF (regenerated from what the client
confirmed) + a follow-up calendar entry on the promised payment date.
"""

SCRIPT = {
    "name": "invoice_chase",
    "opening": (
        "Hi {contact}, this is a call from {business} regarding an "
        "outstanding invoice. {context} Do you have a moment?"
    ),
    "steps": [
        {
            "goal": "Confirm the client recognizes the invoice and its amount.",
            "prompt": "I'm calling about the invoice we sent — can you confirm you've received it?",
        },
        {
            "goal": "Get a firm payment date or an explanation for the delay.",
            "prompt": "When can we expect payment on this?",
        },
        {
            "goal": "Confirm the payment method or any dispute on the amount.",
            "prompt": "Will that be the same payment method as before, or is there anything about the amount you'd like to flag?",
        },
    ],
    "closing": "Great, thank you — I'll follow up with a confirmation. Have a good day.",
    "extract_fields": {
        "outcome": "paid / promised-to-pay / disputed / no-answer / refused",
        "next_step": "what to do next, e.g. 'follow up on 2026-08-25'",
        "summary": "1-2 sentence summary",
        "invoice": {
            "number": "string",
            "client": "string",
            "currency": "string, default AED",
            "items": "[{description, qty, unit_price}]",
            "due_date": "YYYY-MM-DD, the promised payment date",
        },
        "event": {
            "summary": "e.g. 'Follow up: invoice payment from <client>'",
            "start": "YYYY-MM-DD HH:MM, the promised payment date at 09:00",
            "duration_minutes": 15,
            "description": "reason for follow-up",
        },
    },
    "produces_invoice": True,
    "produces_calendar": True,
}
