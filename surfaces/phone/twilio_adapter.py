"""Real phone line via Twilio Programmable Voice.

Uses Twilio's built-in TTS (<Say>) and speech recognition (<Gather
input="speech">) — no separate STT/TTS pipeline or raw audio streaming
needed. twilio_server.py runs the webhook side that Twilio talks to;
twilio_state.py bridges that back to this adapter's synchronous
dial/say/listen/hangup, which is all calls/runner.py knows about.

Requires in .env:
  TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
  TWILIO_WEBHOOK_BASE_URL  — a public URL reaching this machine's
                             TWILIO_WEBHOOK_PORT (default 8080), e.g. an
                             ngrok tunnel: `ngrok http 8080`, then set
                             TWILIO_WEBHOOK_BASE_URL to the https URL it
                             prints. Twilio must be able to reach this
                             URL from the internet to drive the call.

Set PHONE_ADAPTER=twilio in .env to select this adapter.
"""

import base64

import requests

from brain import config
from . import twilio_state
from .adapter import CallEnded, PhoneAdapter

TWILIO_CALLS_URL = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls.json"
TWILIO_CALL_URL = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls/{call_sid}.json"
DIAL_TIMEOUT = 60   # seconds to wait for the call to be answered
LISTEN_TIMEOUT = 200  # seconds to wait for the callee's next reply


class TwilioAdapter(PhoneAdapter):
    def __init__(self):
        self._sid = config.get("TWILIO_ACCOUNT_SID")
        self._token = config.get("TWILIO_AUTH_TOKEN")
        self._from = config.get("TWILIO_FROM_NUMBER")
        missing = [name for name, val in [
            ("TWILIO_ACCOUNT_SID", self._sid),
            ("TWILIO_AUTH_TOKEN", self._token),
            ("TWILIO_FROM_NUMBER", self._from),
        ] if not val]
        if missing:
            raise RuntimeError(
                f"PHONE_ADAPTER=twilio but missing from .env: {', '.join(missing)}"
            )
        self._call_id = None

    def dial(self, number: str) -> None:
        from . import twilio_server
        twilio_server.start_server()

        base_url = config.get("TWILIO_WEBHOOK_BASE_URL", "").rstrip("/")
        if not base_url:
            raise RuntimeError(
                "TWILIO_WEBHOOK_BASE_URL not set in .env — Twilio needs a "
                "public URL to reach this machine (e.g. an ngrok tunnel)."
            )

        call_id = twilio_state.new_call(number)
        self._call_id = call_id

        auth = base64.b64encode(f"{self._sid}:{self._token}".encode()).decode()
        resp = requests.post(
            TWILIO_CALLS_URL.format(sid=self._sid),
            headers={"Authorization": f"Basic {auth}"},
            data={
                "To": number,
                "From": self._from,
                "Url": f"{base_url}/twilio/voice/{call_id}",
                "StatusCallback": f"{base_url}/twilio/status/{call_id}",
                "StatusCallbackEvent": "initiated ringing answered completed",
                "StatusCallbackMethod": "POST",
            },
            timeout=30,
        )
        if resp.status_code >= 300:
            twilio_state.discard(call_id)
            raise CallEnded(f"Twilio call create failed: {resp.status_code} {resp.text[:300]}")

        state = twilio_state.get(call_id)
        if not state.resolved.wait(timeout=DIAL_TIMEOUT):
            twilio_state.mark_ended(call_id, "timed out waiting for answer")
            raise CallEnded("timed out waiting for the call to be answered")
        if state.ended.is_set():
            raise CallEnded(f"call did not connect: {state.end_reason}")

    def say(self, text: str) -> None:
        twilio_state.push_outbound(self._call_id, text)

    def listen(self) -> str:
        reply = twilio_state.pop_inbound(self._call_id, timeout=LISTEN_TIMEOUT)
        if reply is twilio_state.HANGUP:
            raise CallEnded("call ended")
        return reply

    def hangup(self) -> None:
        state = twilio_state.get(self._call_id)
        if state and not state.ended.is_set():
            twilio_state.push_outbound(self._call_id, twilio_state.HANGUP)
        # Safety net: also end the call via REST in case nothing is
        # polling for the sentinel (e.g. the callee already hung up).
        sid = state.call_sid if state else None
        if sid:
            auth = base64.b64encode(f"{self._sid}:{self._token}".encode()).decode()
            try:
                requests.post(
                    TWILIO_CALL_URL.format(sid=self._sid, call_sid=sid),
                    headers={"Authorization": f"Basic {auth}"},
                    data={"Status": "completed"},
                    timeout=10,
                )
            except requests.RequestException:
                pass
        if self._call_id:
            twilio_state.mark_ended(self._call_id, "hangup")
            twilio_state.discard(self._call_id)
