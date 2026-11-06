"""The chat API kit: serializers, views, problem+json errors, the stream and its schema, over a `ChatService`.

    from django_cfg.modules.django_llm.agent.chat.api import urls
    urlpatterns = urls(service, operation_id_prefix="assistant", tag="assistant")

Import this only in a project that serves the chat over HTTP (it needs DRF and drf-spectacular). See
`../@docs/chat-api-kit.md`.
"""

from django_cfg.modules.django_llm.agent.chat.api.problems import CODES, PROBLEM_MEDIA_TYPE, ServiceUnavailable
from django_cfg.modules.django_llm.agent.chat.api.urls import urls

__all__ = ["CODES", "PROBLEM_MEDIA_TYPE", "ServiceUnavailable", "urls"]
