"""Call a business to book or reschedule an appointment.

Receipts: outcome note + confirmed .ics calendar entry.
"""

SCRIPT = {
    "name": "appointment_booking",
    "opening": (
        "Hi, this is a call on behalf of {business} to book an appointment "
        "with {contact}. {context}"
    ),
    "steps": [
        {
            "goal": "Find out what dates/times are available.",
            "prompt": "What availability do you have in the next week or two?",
        },
        {
            "goal": "Lock in a specific date and time.",
            "prompt": "That works — can we confirm that slot?",
        },
        {
            "goal": "Get any prep instructions, location, or requirements for the appointment.",
            "prompt": "Is there anything we need to bring or prepare beforehand?",
        },
    ],
    "closing": "Perfect, that's confirmed. Thank you, see you then.",
    "extract_fields": {
        "outcome": "booked / rescheduled / no-availability / no-answer",
        "next_step": "what to do next",
        "summary": "1-2 sentence summary",
        "event": {
            "summary": "e.g. 'Appointment with <contact>'",
            "start": "YYYY-MM-DD HH:MM",
            "duration_minutes": "int, default 60",
            "location": "string if given",
            "description": "prep instructions or requirements",
        },
    },
    "produces_invoice": False,
    "produces_calendar": True,
}
