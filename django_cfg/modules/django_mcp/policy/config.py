"""Positive read grants; model validation happens before an ORM query."""

import re
from typing import Dict, List, Union

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

Scalar = Union[str, bool, int, FiniteFloat, None]
FIELD = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
READ_TOOLS = frozenset({"query_model", "get_object", "list_apps", "get_model_schema"})
LOOKUPS = frozenset({"exact", "iexact", "contains", "icontains", "gt", "gte", "lt", "lte", "isnull", "in"})
MAX_FILTERS, MAX_TEXT, MAX_IN, MAX_OFFSET = 12, 4096, 25, 1000
MAX_ROWS, MAX_BYTES = 25, 128 * 1024


def sensitive_name(name: str) -> bool:
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()
    return bool(re.search(r"password|passwd|secret|token|session|credential|apikey|otp|oauth|pkce", words)) or "key" in re.split(r"[^a-z0-9]+", words)


class ScalarReadPolicy(BaseModel):
    """A scalar projection, approved predicates/order and immutable equality scope."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, hide_input_in_errors=True)
    fields: List[str] = Field(min_length=1, max_length=64)
    filter_fields: List[str] = Field(default_factory=list, max_length=64)
    order_fields: List[str] = Field(default_factory=list, max_length=64)
    scope: Dict[str, Scalar] = Field(default_factory=dict, max_length=MAX_FILTERS)

    @model_validator(mode="after")
    def _closed_grant(self) -> "ScalarReadPolicy":
        for names in [self.fields, self.filter_fields, self.order_fields, list(self.scope)]:
            if len(set(names)) != len(names):
                raise ValueError("Duplicate read-policy field")
            if any(not FIELD.fullmatch(n) or "__" in n or sensitive_name(n) for n in names):
                raise ValueError("Read policy requires nonsensitive scalar field names")
        approved = set(self.fields)
        if not set(self.filter_fields + self.order_fields + list(self.scope)).issubset(approved):
            raise ValueError("Filter, order and scope fields must be in the output projection")
        if any(isinstance(v, str) and len(v) > MAX_TEXT for v in self.scope.values()):
            raise ValueError("Fixed read scope exceeds the scalar bound")
        return self


class ReadPolicyError(ValueError):
    """Static public refusal, never an ORM exception or a record value."""

    def __init__(self, message: str = "Model read is outside its scalar policy.") -> None:
        super().__init__(message)
