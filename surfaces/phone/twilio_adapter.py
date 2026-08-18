"""Placeholder for the real phone line (Phase 2).

Wiring plan when a provider account exists:
  - Twilio Programmable Voice: REST API places the outbound call, a
    Media Streams websocket carries audio both ways.
  - say():   text -> TTS (Twilio <Say>, or ElevenLabs audio into the stream)
  - listen():stream audio -> STT (Deepgram / Whisper) until end-of-utterance
  - Env:     TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER

Nothing else in the pack changes: calls/runner.py already speaks only
the PhoneAdapter interface.
"""

from .adapter import PhoneAdapter


class TwilioAdapter(PhoneAdapter):
    _MSG = ("Real phone line not wired yet — this pack ships with "
            "PHONE_ADAPTER=stub. See surfaces/phone/twilio_adapter.py "
            "for the Phase 2 wiring plan.")

    def dial(self, number: str) -> None:
        raise NotImplementedError(self._MSG)

    def say(self, text: str) -> None:
        raise NotImplementedError(self._MSG)

    def listen(self) -> str:
        raise NotImplementedError(self._MSG)

    def hangup(self) -> None:
        raise NotImplementedError(self._MSG)
