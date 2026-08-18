"""Call a supplier or seller to get a price/availability quote.

Receipts: outcome note with the structured quote (no PDF/calendar —
just a clean record in the vault to compare later).
"""

SCRIPT = {
    "name": "price_inquiry",
    "opening": (
        "Hi, I'm calling about {context}, is this {contact}? I had a "
        "question about price and availability."
    ),
    "steps": [
        {
            "goal": "Confirm the item/service is still available.",
            "prompt": "Is it still available?",
        },
        {
            "goal": "Get the price and whether it's negotiable.",
            "prompt": "What's the price, and is there any flexibility on it?",
        },
        {
            "goal": "Get condition/terms/timeline details relevant to the item.",
            "prompt": "Can you tell me a bit more about the condition and how soon this could happen?",
        },
    ],
    "closing": "That's really helpful, thank you for your time.",
    "extract_fields": {
        "outcome": "quote-received / unavailable / no-answer / needs-followup",
        "next_step": "what to do next",
        "summary": "1-2 sentence summary",
        "quote": {
            "item": "string",
            "price": "number",
            "currency": "string, default AED",
            "negotiable": "true/false",
            "condition_or_terms": "string",
            "availability": "string",
        },
    },
    "produces_invoice": False,
    "produces_calendar": False,
}
