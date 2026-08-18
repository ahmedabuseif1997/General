"""Webhook server for the Twilio phone adapter.

Twilio calls are webhook-driven, not blocking function calls: when the
callee answers, Twilio POSTs to our /voice URL and expects TwiML back;
after the callee speaks, it POSTs to /gather with the transcript and
again expects TwiML. twilio_state.py bridges that to the synchronous
dial/say/listen/hangup interface the rest of the pack uses.

A single line can take a while to produce (the brain call in
calls/runner.py can run up to ~120s), which is longer than Twilio's
webhook response budget. So instead of blocking one request for the
full duration, each handler blocks briefly (POLL_SECONDS), and if the
next line isn't ready yet, responds with a short <Pause> + <Redirect>
back to /wait, which polls again. This is Twilio's standard pattern for
a slow-to-produce response.

Not started directly — TwilioAdapter starts it in a background thread
on first use. See twilio_adapter.py.
"""

import base64
import hashlib
import hmac
import threading
from xml.sax.saxutils import escape

from flask import Flask, Response, request

from brain import config
from . import twilio_state

app = Flask(__name__)

POLL_SECONDS = 4          # each handler blocks up to this long for a line
MAX_POLL_ROUNDS = 40      # ~40 * (POLL_SECONDS + 1s pause) ≈ 200s ceiling


def _base_url() -> str:
    url = config.get("TWILIO_WEBHOOK_BASE_URL", "").rstrip("/")
    if not url:
        raise RuntimeError("TWILIO_WEBHOOK_BASE_URL not set in .env — "
                          "Twilio needs a public URL to call back into "
                          "(e.g. an ngrok tunnel to this server's port)")
    return url


def _valid_signature(req) -> bool:
    """Verify the X-Twilio-Signature header per Twilio's documented
    request-validation algorithm, so only Twilio (holder of our auth
    token) can drive the call — the webhook URL is public once tunnelled."""
    auth_token = config.get("TWILIO_AUTH_TOKEN")
    if not auth_token:
        return False
    signature = req.headers.get("X-Twilio-Signature", "")
    url = _base_url() + req.path
    data = url
    for key in sorted(req.form.keys()):
        data += key + req.form[key]
    expected = base64.b64encode(
        hmac.new(auth_token.encode(), data.encode(), hashlib.sha1).digest()
    ).decode()
    return hmac.compare_digest(expected, signature)


def _twiml(body: str) -> Response:
    return Response(
        f'<?xml version="1.0" encoding="UTF-8"?><Response>{body}</Response>',
        mimetype="text/xml",
    )


def _gather_block(call_id: str) -> str:
    action = escape(f"{_base_url()}/twilio/gather/{call_id}")
    return (f'<Gather input="speech" method="POST" speechTimeout="auto" '
           f'language="en-US" action="{action}"/>')


def _say_and_continue(call_id: str, text: str, hangup: bool) -> Response:
    say = f"<Say>{escape(text)}</Say>" if text else ""
    if hangup:
        return _twiml(f"{say}<Hangup/>")
    return _twiml(f"{say}{_gather_block(call_id)}")


def _wait_or_respond(call_id: str, round_no: int) -> Response:
    state = twilio_state.get(call_id)
    if state is None:
        return _twiml("<Hangup/>")

    text, hangup = twilio_state.pop_outbound_nowait(call_id, timeout=POLL_SECONDS)
    if text is not None or hangup:
        return _say_and_continue(call_id, text or "", hangup)

    if round_no >= MAX_POLL_ROUNDS:
        twilio_state.mark_ended(call_id, "timed out waiting for a response")
        return _twiml("<Say>Sorry, I need to call you back.</Say><Hangup/>")

    redirect = escape(f"{_base_url()}/twilio/wait/{call_id}/{round_no + 1}")
    return _twiml(f'<Pause length="1"/><Redirect method="POST">{redirect}</Redirect>')


@app.route("/twilio/voice/<call_id>", methods=["POST"])
def voice(call_id: str):
    if not _valid_signature(request):
        return Response(status=403)
    twilio_state.mark_connected(call_id)
    state = twilio_state.get(call_id)
    if state is not None:
        state.call_sid = request.form.get("CallSid")
    return _wait_or_respond(call_id, round_no=0)


@app.route("/twilio/gather/<call_id>", methods=["POST"])
def gather(call_id: str):
    if not _valid_signature(request):
        return Response(status=403)
    speech = request.form.get("SpeechResult", "")
    twilio_state.push_inbound(call_id, speech)
    return _wait_or_respond(call_id, round_no=0)


@app.route("/twilio/wait/<call_id>/<int:round_no>", methods=["POST"])
def wait(call_id: str, round_no: int):
    if not _valid_signature(request):
        return Response(status=403)
    return _wait_or_respond(call_id, round_no)


@app.route("/twilio/status/<call_id>", methods=["POST"])
def status(call_id: str):
    if not _valid_signature(request):
        return Response(status=403)
    call_status = request.form.get("CallStatus", "")
    if call_status in ("completed", "busy", "failed", "no-answer", "canceled"):
        twilio_state.mark_ended(call_id, call_status)
    return Response(status=204)


_server_thread = None
_server_lock = threading.Lock()


def start_server() -> None:
    """Idempotent: starts the webhook server in a background thread once."""
    global _server_thread
    with _server_lock:
        if _server_thread is not None:
            return
        port = int(config.get("TWILIO_WEBHOOK_PORT", "8080"))
        _server_thread = threading.Thread(
            target=lambda: app.run(host="0.0.0.0", port=port,
                                   threaded=True, use_reloader=False),
            daemon=True,
        )
        _server_thread.start()
