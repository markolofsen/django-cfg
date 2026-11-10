"""`urls(service, ...)`: the whole chat contract as URL patterns.

    # urls.py of the host
    from django.urls import include, path
    from django_cfg.modules.django_llm.agent.chat.api import urls as chat_urls

    urlpatterns = [path("apix/assistant/", include((chat_urls(service, operation_id_prefix="assistant", tag="assistant"), "assistant")))]

Routes (trailing slash on by default; `trailing_slash=False` for hosts whose client calls them bare):

    GET  threads            POST threads            GET threads/<uuid>            POST threads/<uuid>/messages
    GET  threads/<uuid>/messages/<uuid>/stream?after=&text_offset=   (follow a running answer: a second tab, a reconnect)
    POST threads/<uuid>/messages/<uuid>/cancel                       (stop a running answer: 202 cancelling, or 200 with its status)
    POST threads/<uuid>/messages/<uuid>/parts/<n>/ack      (the browser's verdict on a ui payload)
    POST attachments (multipart)    DELETE attachments/<uuid>    GET attachments/<uuid>/content    GET attachments/limits
        (404 for a host whose Message has no `attachments` table; a kind with no `ChatKind.attachments` policy takes no file)
    GET  search?q=          (only when `search=` is passed)
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from django.urls import URLPattern, path
from rest_framework.permissions import AllowAny, IsAuthenticated

from django_cfg.modules.django_llm.agent.chat.api import views
from django_cfg.modules.django_llm.agent.chat.service import ChatService


def urls(
    service: ChatService,
    *,
    operation_id_prefix: str,
    tag: str,
    trailing_slash: bool = True,
    default_kind: str | None = None,
    throttle_classes: Sequence[type] = (),
    send_throttle_classes: Sequence[type] | None = None,
    authentication_classes: Sequence[type] | None = None,
    permission_classes: Sequence[type] | None = None,
    gate: Callable[[Any], None] | None = None,
    search: Callable[..., list] | None = None,
) -> list[URLPattern]:
    """URL patterns for the chat API over `service`.

    `operation_id_prefix` and `tag` name the operations in the OpenAPI schema (`<prefix>_threads_list` ...), so a host keeps the
    names its generated client already uses. `throttle_classes` guard every route, `send_throttle_classes` (default: the same) the
    stream route alone. `authentication_classes` defaults to the project's DRF settings; `permission_classes` defaults to `IsAuthenticated`. `default_kind`
    lets "new chat" omit `kind`. `gate(request)` runs after authentication and throttles on every route: raise
    `ServiceUnavailable` for a kill switch or a spent budget (503) or any chat error. `search(user, query, *, kind, limit)` mounts
    `GET search` (cross-thread search by meaning, `chat.vectors`); without it the route does not exist.
    """
    common: dict[str, Any] = {
        "service": service,
        "operation_id_prefix": operation_id_prefix,
        "tag": tag,
        "default_kind": default_kind,
        "gate": gate,
    }
    if authentication_classes is not None:
        common["authentication_classes"] = list(authentication_classes)
    # A chat thread is its owner's data: closed unless the host says otherwise. The project's DRF default is often AllowAny
    # (Docman and GPT-Kino both let anonymous callers in until they passed this by hand).
    common["permission_classes"] = list(permission_classes) if permission_classes is not None else [IsAuthenticated]
    reading = {**common, "throttle_classes": list(throttle_classes)}
    sending = {**common, "throttle_classes": list(throttle_classes if send_throttle_classes is None else send_throttle_classes)}
    end = "/" if trailing_slash else ""
    routes = [
        path(f"threads{end}", views.ThreadsView.as_view(**reading), name="threads"),
        path(f"threads/<uuid:thread_id>{end}", views.ThreadView.as_view(**reading), name="thread"),
        path(f"threads/<uuid:thread_id>/messages{end}", views.MessagesView.as_view(**sending), name="messages"),
        path(f"threads/<uuid:thread_id>/messages/<uuid:message_id>/stream{end}", views.MessageStreamView.as_view(**reading), name="message-stream"),
        path(f"threads/<uuid:thread_id>/messages/<uuid:message_id>/cancel{end}", views.MessageCancelView.as_view(**reading), name="message-cancel"),
        path(f"threads/<uuid:thread_id>/messages/<uuid:message_id>/parts/<int:index>/ack{end}", views.PartAckView.as_view(**reading), name="part-ack"),
    ]
    if service.attachment_model is not None:  # a host without the table keeps its routes byte for byte
        routes += [
            path(f"attachments{end}", views.AttachmentsView.as_view(**sending), name="attachments"),
            path(f"attachments/limits{end}", views.AttachmentLimitsView.as_view(**reading), name="attachment-limits"),
            path(f"attachments/<uuid:attachment_id>{end}", views.AttachmentView.as_view(**reading), name="attachment"),
            path(f"attachments/<uuid:attachment_id>/content{end}", views.AttachmentContentView.as_view(**{**reading, "permission_classes": [AllowAny]}), name="attachment-content"),
        ]
    if search is not None:
        routes.append(path(f"search{end}", views.SearchView.as_view(**reading, search=search), name="search"))
    return routes
