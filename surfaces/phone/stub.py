"""Simulated phone line.

ConsoleStubAdapter: you play the callee at the keyboard. Type the other
side's replies; type /hangup to end the call. Lets the whole pipeline —
script, dialogue, outcome extraction, receipts — run end-to-end with no
telephony account.
"""

from .adapter import CallEnded, PhoneAdapter


class ConsoleStubAdapter(PhoneAdapter):
    def dial(self, number: str) -> None:
        print(f"\n☎  [stub line] dialing {number} … connected.")
        print("   (you are the callee — type replies, /hangup to end)\n")

    def say(self, text: str) -> None:
        print(f"AGENT:  {text}")

    def listen(self) -> str:
        try:
            reply = input("CALLEE> ").strip()
        except (EOFError, KeyboardInterrupt):
            raise CallEnded from None
        if reply.lower() in ("/hangup", "/end"):
            raise CallEnded
        return reply

    def hangup(self) -> None:
        print("☎  [stub line] call ended.\n")
