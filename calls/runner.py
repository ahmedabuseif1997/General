"""Runs one outbound-call script end-to-end over a PhoneAdapter.

Loop: dial -> greet -> for each of the script's steps, say the prompt,
listen for a reply, hand (script, prompt, reply) to the brain to decide
what to say next and whether a step's data has been captured -> once all
steps are captured (or the callee hangs up), hang up, ask the brain to
extract structured fields from the transcript, then hand off to
receipts.py for the outcome note (+ invoice PDF / .ics as the script
calls for) and deliver().

CLI:  python3 -m calls.runner <script_name> --contact "Name" --number "+971..." [--context "free text"]
Scripts live in calls/scripts/*.py as SCRIPT dicts (see calls/scripts/README in each file's docstring).
"""

import argparse
import importlib
import json
import sys

from brain import config, vault
from brain.claude_client import BrainUnavailable, run_brain
from brain.receipts import build_ics, build_invoice_pdf, deliver, write_outcome_note
from surfaces.phone.adapter import CallEnded, get_adapter

SCRIPT_NAMES = ["invoice_chase", "appointment_booking", "price_inquiry", "reservation"]


def load_script(name: str) -> dict:
    if name not in SCRIPT_NAMES:
        sys.exit(f"unknown script {name!r} — choose from {SCRIPT_NAMES}")
    mod = importlib.import_module(f"calls.scripts.{name}")
    return mod.SCRIPT


def run_call(script: dict, contact: str, number: str, context: str) -> list:
    """Drive the call; return the transcript as [(who, text), ...]."""
    adapter = get_adapter()
    transcript = []

    def agent_say(text: str) -> None:
        adapter.say(text)
        transcript.append(("agent", text))

    adapter.dial(number)
    opening = script["opening"].format(business=config.get("BUSINESS_NAME", "us"),
                                       contact=contact, context=context)
    agent_say(opening)

    try:
        for step in script["steps"]:
            agent_say(step["prompt"])
            reply = adapter.listen()
            transcript.append(("callee", reply))

            brain_prompt = (
                f"You are conducting a phone call using the '{script['name']}' script.\n"
                f"Context: {context or '(none given)'}\n"
                f"Current step goal: {step['goal']}\n"
                f"The callee just said: \"{reply}\"\n\n"
                "Reply with ONLY a JSON object: "
                '{"say_next": "<one short natural sentence to say now, '
                'or empty string if the step is fully answered and we should move on>", '
                '"satisfied": true/false}'
            )
            try:
                raw = run_brain(brain_prompt, timeout=120)
                decision = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
            except (BrainUnavailable, ValueError, json.JSONDecodeError):
                decision = {"say_next": "", "satisfied": True}

            if decision.get("say_next"):
                agent_say(decision["say_next"])
                # give the step one more turn to land
                reply2 = adapter.listen()
                transcript.append(("callee", reply2))

        agent_say(script["closing"])
    except CallEnded:
        transcript.append(("system", "call ended by callee"))
    finally:
        adapter.hangup()

    return transcript


def extract_fields(script: dict, transcript: list) -> dict:
    convo = "\n".join(f"{who}: {text}" for who, text in transcript)
    prompt = (
        f"A phone call just happened using the '{script['name']}' script.\n"
        f"Transcript:\n{convo}\n\n"
        f"Extract these fields as JSON: {script['extract_fields']}\n"
        'Always include "outcome" (short phrase), "next_step" (short phrase or "none"), '
        '"summary" (1-2 sentences). Reply with ONLY the JSON object, no prose.'
    )
    try:
        raw = run_brain(prompt, timeout=120)
        return json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
    except (BrainUnavailable, ValueError, json.JSONDecodeError):
        return {"outcome": "unknown — brain extraction failed",
                "next_step": "review transcript manually", "summary": ""}


def main() -> None:
    parser = argparse.ArgumentParser(prog="calls.runner")
    parser.add_argument("script", choices=SCRIPT_NAMES)
    parser.add_argument("--contact", required=True)
    parser.add_argument("--number", required=True)
    parser.add_argument("--context", default="")
    args = parser.parse_args()

    script = load_script(args.script)
    transcript = run_call(script, args.contact, args.number, args.context)
    fields = extract_fields(script, transcript)

    note_path = write_outcome_note(args.script, args.contact, transcript, fields)
    vault.log_action(f"call [{args.script}] to {args.contact} ({args.number}): "
                     f"{fields.get('outcome', '?')}")

    files = [note_path]
    if script.get("produces_invoice") and fields.get("invoice"):
        files.append(build_invoice_pdf(fields["invoice"]))
    if script.get("produces_calendar") and fields.get("event"):
        files.append(build_ics(fields["event"]))

    summary = (f"📞 {script['name'].replace('_', ' ').title()} — {args.contact}\n"
              f"Outcome: {fields.get('outcome', '?')}\n"
              f"Next step: {fields.get('next_step', '—')}\n\n"
              f"{fields.get('summary', '')}")
    deliver(summary, files)
    print(f"\ndone — outcome note at {note_path}")


if __name__ == "__main__":
    main()
