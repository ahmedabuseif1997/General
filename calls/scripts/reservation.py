"""Call to make a restaurant/hotel/service reservation.

Receipts: outcome note + confirmed .ics calendar entry.
"""

SCRIPT = {
    "name": "reservation",
    "opening": (
        "Hi, I'd like to make a reservation. {context}"
    ),
    "steps": [
        {
            "goal": "State party size and preferred date/time, get confirmation or alternatives.",
            "prompt": "Do you have availability for the date and time I mentioned?",
        },
        {
            "goal": "Lock in the reservation details.",
            "prompt": "Can we confirm that booking?",
        },
        {
            "goal": "Note any special requests and the name/contact for the reservation.",
            "prompt": "I'd like to note a couple of special requests — is that alright, and what name should this be under?",
        },
    ],
    "closing": "Wonderful, thank you — looking forward to it.",
    "extract_fields": {
        "outcome": "confirmed / alternative-offered / unavailable / no-answer",
        "next_step": "what to do next",
        "summary": "1-2 sentence summary",
        "event": {
            "summary": "e.g. 'Reservation at <place> for <party_size>'",
            "start": "YYYY-MM-DD HH:MM",
            "duration_minutes": "int, default 90",
            "location": "string",
            "description": "party size and special requests",
        },
    },
    "produces_invoice": False,
    "produces_calendar": True,
}
