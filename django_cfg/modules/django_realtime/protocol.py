"""Wire protocol v1: every frame, the closed code sets, the close codes. The only place the wire shape is defined.

JSON text frames, each with `op`. Unknown fields are ignored; an unknown `op` is an `error` frame.
"""

from __future__ import annotations

import json
import re
from enum import IntEnum
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

PROTOCOL_VERSION = 1

#: A concrete topic name: `orders:42`, `demo.ping`.
TOPIC_RE = re.compile(r"^[a-z0-9_.-]+(:[A-Za-z0-9_.-]+)*$")
#: A connection id as `hello.cid` issues it and `X-Realtime-Cid` carries it back.
CID_RE = re.compile(r"^[A-Za-z0-9]{8,32}$")

SubErrCode = Literal["forbidden", "unknown_topic", "invalid", "limit", "timeout"]
ErrorCode = Literal["bad_json", "bad_frame", "unknown_op", "too_large", "auth_late"]


class Close(IntEnum):
    """Close codes. The client reconnects on everything except AUTH, ORIGIN and LIMIT."""

    AUTH = 4401           # auth required or failed
    ORIGIN = 4403         # origin refused
    AUTH_TIMEOUT = 4408   # no first frame within auth_timeout
    REVOKED = 4419        # credentials expired or revoked: refresh over HTTP, reconnect at once
    LIMIT = 4429          # connection limit, or an inbound frame flood
    SERVER_ERROR = 4500
    KEEPALIVE = 1011      # sent by uvicorn when its protocol ping goes unanswered
    RESTART = 1012        # server restart (shutdown)
    TRY_AGAIN = 1013      # slow consumer: the send queue overflowed; reconnect and replay with `since`


class _Frame(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)


# ---------------------------------------------------------------- client -> server

class AuthFrame(_Frame):
    op: Literal["auth"]
    # Absent: settle on the handshake's own credentials (cookies) now, without waiting out the auth window.
    token: Optional[str] = Field(default=None, min_length=1, max_length=8192)


class SubFrame(_Frame):
    op: Literal["sub"]
    id: int
    topic: str = Field(min_length=1, max_length=512)
    since: Optional[str] = Field(default=None, max_length=128)


class UnsubFrame(_Frame):
    op: Literal["unsub"]
    topic: str = Field(min_length=1, max_length=512)


class PingFrame(_Frame):
    """Client keepalive every `hello.ping` seconds; answered with `pong`."""

    op: Literal["ping"]


ClientFrame = Annotated[Union[AuthFrame, SubFrame, UnsubFrame, PingFrame], Field(discriminator="op")]
_CLIENT_OPS = frozenset({"auth", "sub", "unsub", "ping"})
_client_adapter: TypeAdapter = TypeAdapter(ClientFrame)


class ProtocolError(Exception):
    """A client frame that cannot be used; answered with an `error` frame, the socket stays open."""

    def __init__(self, code: ErrorCode, detail: str = ""):
        super().__init__(detail or code)
        self.code = code
        self.detail = detail


def parse_client_frame(text: str):
    """One inbound text frame -> a frame model, or ProtocolError."""
    try:
        raw = json.loads(text)
    except ValueError as exc:
        raise ProtocolError("bad_json", str(exc)) from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("op"), str):
        raise ProtocolError("bad_frame", "a frame is a JSON object with a string `op`")
    if raw["op"] not in _CLIENT_OPS:
        raise ProtocolError("unknown_op", raw["op"][:64])
    try:
        return _client_adapter.validate_python(raw)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(p) for p in first.get("loc", ())[1:])
        raise ProtocolError("bad_frame", f"{where}: {first.get('msg', 'invalid')}") from exc


# ---------------------------------------------------------------- server -> client

class Hello(_Frame):
    op: Literal["hello"] = "hello"
    v: int = PROTOCOL_VERSION
    user: Union[int, str, None]
    ping: int  # the interval the client pings at, seconds
    cid: str   # this connection's id; send it as `X-Realtime-Cid` so your own publishes are not echoed


class SubOk(_Frame):
    op: Literal["sub_ok"] = "sub_ok"
    id: int
    topic: str
    offset: str
    recovered: Optional[bool] = None  # present only when the `sub` carried `since`


class SubErr(_Frame):
    op: Literal["sub_err"] = "sub_err"
    id: int
    topic: str
    code: SubErrCode


class Msg(_Frame):
    op: Literal["msg"] = "msg"
    topic: str
    offset: str
    data: Any
    origin_cid: Optional[str] = None  # set when the publishing request carried X-Realtime-Cid


class Pong(_Frame):
    op: Literal["pong"] = "pong"


class Error(_Frame):
    op: Literal["error"] = "error"
    code: ErrorCode
    detail: Optional[str] = None


_OMIT_IF_NONE = {"recovered", "detail", "origin_cid"}


def encode(frame: _Frame) -> str:
    """Serialise a server frame. `recovered`, `detail`, `origin_cid` are left out when unset; `user: null` stays."""
    data = frame.model_dump(mode="json")
    for key in _OMIT_IF_NONE:
        if key in data and data[key] is None:
            del data[key]
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


__all__ = [
    "CID_RE", "PROTOCOL_VERSION", "TOPIC_RE", "AuthFrame", "Close", "Error", "ErrorCode", "Hello", "Msg",
    "PingFrame", "Pong", "ProtocolError", "SubErr", "SubErrCode", "SubFrame", "SubOk", "UnsubFrame",
    "encode", "parse_client_frame",
]
