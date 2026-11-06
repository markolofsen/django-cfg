"""OpenAPI for the kit: operation ids and tags come from the host (`operation_id_prefix`, `tag`), so a generated client keeps the
names it already has. Each view declares `docs` (one `Doc` per HTTP method); this schema class turns them into the operation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import OpenApiParameter

from django_cfg.modules.django_llm.agent.chat.api.problems import PROBLEM_MEDIA_TYPE, ProblemSerializer


@dataclass(frozen=True)
class Doc:
    suffix: str  # operation id is `<operation_id_prefix>_<suffix>`
    summary: str
    responses: dict
    request: Any = None
    parameters: tuple = field(default_factory=tuple)


def problems(*codes: int) -> dict:
    """`{status: ProblemSerializer}` as `application/problem+json` responses."""
    return {(code, PROBLEM_MEDIA_TYPE): ProblemSerializer for code in codes}


RETRY_AFTER = OpenApiParameter("Retry-After", int, OpenApiParameter.HEADER, response=[429, 503], description="Seconds to wait before trying again.")


class ChatSchema(AutoSchema):
    def _doc(self) -> Doc:
        return self.view.docs[self.method]

    def get_operation_id(self) -> str:
        return f"{self.view.operation_id_prefix}_{self._doc().suffix}"

    def get_tags(self) -> list[str]:
        return [self.view.tag]

    def get_summary(self) -> str:
        return self._doc().summary

    def get_request_serializer(self):
        return self._doc().request

    def get_response_serializers(self):
        return self._doc().responses

    def get_override_parameters(self):
        return list(super().get_override_parameters()) + list(self._doc().parameters)
