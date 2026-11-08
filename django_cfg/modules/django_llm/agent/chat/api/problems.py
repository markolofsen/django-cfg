"""Errors before a stream: `application/problem+json` with the six codes of the widget's wire contract.

Every refusal of the kit has the same body, whichever layer raised it (authentication, a throttle, validation, the
service, a host gate):

    {"type": "about:blank", "title": "Too Many Requests", "status": 429, "code": "rate_limited", "detail": "...", "field"?: "..."}

`code` is what a client reads (`unauthorized`, `busy`, `invalid`, `rate_limited`, `unavailable`, `not_found`); `field`
names the offending input of an `invalid`. A 429 carries `Retry-After`. Anything that is not one of these (a bug) is left
to DRF: a 500, never dressed up as a domain answer. Nothing here puts user text in a message.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone as dt_timezone
from http import HTTPStatus

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from django.utils import timezone
from rest_framework import exceptions as drf
from rest_framework import serializers
from rest_framework.response import Response

from django_cfg.modules.django_llm.agent.chat.errors import (
    Busy,
    ChatError,
    InvalidContext,
    InvalidKind,
    InvalidTurn,
    NotFound,
    QuotaExceeded,
    RateLimited,
    ServiceUnavailable,
)

PROBLEM_MEDIA_TYPE = "application/problem+json"
PRIVATE = "private, no-store"

#: The codes a client may read from a pre-stream refusal (`wire-contract.md`, "Errors before a stream").
CODES = ("unauthorized", "busy", "invalid", "rate_limited", "unavailable", "not_found", "already_given")


@dataclass(frozen=True)
class Problem:
    status: int
    code: str
    detail: str
    field: str | None = None
    retry_after: int | None = None

    def body(self) -> dict:
        body = {"type": "about:blank", "title": HTTPStatus(self.status).phrase, "status": self.status, "code": self.code, "detail": self.detail}
        if self.field:
            body["field"] = self.field
        return body

    def response(self, *, authenticate: str | None = None) -> Response:
        response = Response(self.body(), status=self.status, content_type=PROBLEM_MEDIA_TYPE)
        response["Cache-Control"] = PRIVATE
        if self.retry_after is not None:
            response["Retry-After"] = str(max(1, int(self.retry_after)))
        if authenticate and self.status == 401:
            response["WWW-Authenticate"] = authenticate
        return response


class ProblemSerializer(serializers.Serializer):
    """Schema of every pre-stream refusal (`application/problem+json`)."""

    class Meta:
        ref_name = "ChatProblem"

    type = serializers.CharField(help_text="Always `about:blank`: the code says what happened.")
    title = serializers.CharField(help_text="The HTTP reason phrase.")
    status = serializers.IntegerField()
    code = serializers.ChoiceField(choices=CODES, help_text="What a client branches on.")
    detail = serializers.CharField(help_text="A sentence for a developer. Not for display: the client has its own words per code.")
    field = serializers.CharField(required=False, help_text="The input an `invalid` is about.")


def seconds_until_next_utc_day(now: datetime | None = None) -> int:
    now = (now or timezone.now()).astimezone(dt_timezone.utc)
    tomorrow = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), tzinfo=dt_timezone.utc)
    return math.ceil((tomorrow - now).total_seconds())


def _first_field(errors) -> str | None:
    if isinstance(errors, dict) and errors:
        return str(next(iter(errors)))
    return None


def problem_for(exc: BaseException) -> Problem | None:
    """The problem a known failure maps to, or `None` for anything unexpected."""
    if isinstance(exc, (NotFound, Http404, drf.NotFound)):
        return Problem(404, "not_found", "No such chat.")
    if isinstance(exc, (drf.NotAuthenticated, drf.AuthenticationFailed)):
        return Problem(401, "unauthorized", "Sign in to use the chat.")
    if isinstance(exc, (drf.PermissionDenied, DjangoPermissionDenied)):
        return Problem(403, "unauthorized", "This account may not use the chat.")
    if isinstance(exc, Busy):
        return Problem(409, "busy", "An answer is still being written.")
    if isinstance(exc, RateLimited):
        return Problem(429, "rate_limited", "The daily message allowance is used up.", retry_after=exc.retry_after or seconds_until_next_utc_day())
    if isinstance(exc, QuotaExceeded):
        return Problem(exc.status, exc.code, "The message was refused by the chat's quota.", retry_after=exc.retry_after)
    if isinstance(exc, drf.Throttled):
        return Problem(429, "rate_limited", "Too many requests.", retry_after=math.ceil(exc.wait) if exc.wait else 1)
    if isinstance(exc, ServiceUnavailable):
        return Problem(503, "unavailable", "The chat is not available right now.", retry_after=exc.retry_after)
    if isinstance(exc, InvalidKind):
        return Problem(400, "invalid", "No such chat kind.", field="kind")
    if isinstance(exc, InvalidContext):
        return Problem(400, "invalid", "The context is not valid for this chat.", field=(exc.errors[0]["field"] if exc.errors else "context") or "context")
    if isinstance(exc, InvalidTurn):
        if exc.status == 409:  # a conflict with state the kind holds (`already_given`): its own code, so a client can branch on it
            return Problem(409, exc.code, exc.code, field=exc.field)
        return Problem(exc.status, "invalid", exc.code, field=exc.field)
    if isinstance(exc, drf.ValidationError):
        return Problem(400, "invalid", "The request is not valid.", field=_first_field(exc.detail))
    if isinstance(exc, drf.APIException) and exc.status_code < 500:
        return Problem(exc.status_code, "invalid", HTTPStatus(exc.status_code).phrase)
    return None


class ProblemMixin:
    """For a DRF view: known failures become problem+json; every response is `private, no-store` unless it says otherwise."""

    def handle_exception(self, exc):
        problem = problem_for(exc)
        if problem is None:
            return super().handle_exception(exc)
        return problem.response(authenticate=self.get_authenticate_header(self.request))

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if "Cache-Control" not in response:
            response["Cache-Control"] = PRIVATE
        return response
