"""In-memory call-state registry shared between TwilioAdapter (the caller's
side, running in the call-runner thread) and twilio_server (the webhook
side, running in Flask's request threads).

Each live call gets a CallState with two queues:
  outbound — TwilioAdapter.say() puts lines here; the webhook side reads
             them to build the next <Say> TwiML.
  inbound  — the webhook side puts the callee's SpeechResult here;
             TwilioAdapter.listen() reads it, blocking the runner thread
             until the callee actually says something.

This queue handoff is what lets the webhook-driven Twilio call flow look
like a plain synchronous dial/say/listen/hangup to the rest of the pack.
"""

import queue
import threading
import uuid

HANGUP = object()  # sentinel: "say nothing more, end the call"

_LOCK = threading.Lock()
_CALLS: dict = {}


class CallState:
    def __init__(self, to_number: str):
        self.to_number = to_number
        self.call_sid = None
        self.outbound: "queue.Queue" = queue.Queue()
        self.inbound: "queue.Queue" = queue.Queue()
        self.connected = threading.Event()
        self.ended = threading.Event()
        self.resolved = threading.Event()  # connected OR ended
        self.end_reason = ""


def new_call(to_number: str) -> str:
    call_id = uuid.uuid4().hex
    with _LOCK:
        _CALLS[call_id] = CallState(to_number)
    return call_id


def get(call_id: str) -> "CallState | None":
    with _LOCK:
        return _CALLS.get(call_id)


def discard(call_id: str) -> None:
    with _LOCK:
        _CALLS.pop(call_id, None)


def mark_connected(call_id: str) -> None:
    state = get(call_id)
    if state and not state.ended.is_set():
        state.connected.set()
        state.resolved.set()


def mark_ended(call_id: str, reason: str) -> None:
    state = get(call_id)
    if not state or state.ended.is_set():
        return
    state.end_reason = reason
    state.ended.set()
    state.resolved.set()
    state.inbound.put(HANGUP)  # unblock a runner thread stuck in listen()


def push_outbound(call_id: str, text) -> None:
    state = get(call_id)
    if state:
        state.outbound.put(text)


def pop_outbound_nowait(call_id: str, timeout: float):
    """Return (text_or_None, should_hangup) — a short blocking pop, plus a
    quick follow-up check that coalesces a HANGUP pushed right behind it
    (say(closing) is always immediately followed by hangup() in the
    runner, so the two queue items land back-to-back)."""
    state = get(call_id)
    if not state:
        return None, True
    try:
        item = state.outbound.get(timeout=timeout)
    except queue.Empty:
        return None, False
    if item is HANGUP:
        return None, True
    hangup = False
    try:
        nxt = state.outbound.get(timeout=0.3)
        if nxt is HANGUP:
            hangup = True
        else:
            # shouldn't happen (runner is strictly sequential) — put it back
            state.outbound.put(nxt)
    except queue.Empty:
        pass
    return item, hangup


def push_inbound(call_id: str, text: str) -> None:
    state = get(call_id)
    if state:
        state.inbound.put(text)


def pop_inbound(call_id: str, timeout: float):
    state = get(call_id)
    if not state:
        return HANGUP
    try:
        return state.inbound.get(timeout=timeout)
    except queue.Empty:
        return HANGUP
