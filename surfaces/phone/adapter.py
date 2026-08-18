"""Phone line abstraction.

The call runner only ever talks to this interface, so swapping the stub
for a real line (Twilio, Vonage, SIP) later touches nothing else.
Select with PHONE_ADAPTER in .env: "stub" (default) or "twilio".
"""

from abc import ABC, abstractmethod

from brain import config


class CallEnded(Exception):
    """Raised by listen() when the far side hangs up."""


class PhoneAdapter(ABC):
    @abstractmethod
    def dial(self, number: str) -> None:
        """Place the call and block until answered (or raise CallEnded)."""

    @abstractmethod
    def say(self, text: str) -> None:
        """Speak one agent line to the callee."""

    @abstractmethod
    def listen(self) -> str:
        """Return the callee's next utterance; raise CallEnded on hangup."""

    @abstractmethod
    def hangup(self) -> None:
        """End the call."""


def get_adapter() -> PhoneAdapter:
    name = config.get("PHONE_ADAPTER", "stub").lower()
    if name == "stub":
        from .stub import ConsoleStubAdapter
        return ConsoleStubAdapter()
    if name == "twilio":
        from .twilio_adapter import TwilioAdapter
        return TwilioAdapter()
    raise ValueError(f"unknown PHONE_ADAPTER: {name!r}")
