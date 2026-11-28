"""Resolve concrete scalar columns and serialize them without related-object reads."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Iterable, Mapping
from django.db.models import Model, Field, ForeignKey, OneToOneField

if TYPE_CHECKING:
    from django_cfg.modules.django_mcp.__cfg__ import ModelMCPConfig
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

from .config import MAX_TEXT, ReadPolicyError, Scalar, sensitive_name

SCALAR_TYPES = frozenset({
    "AutoField", "BigAutoField", "SmallAutoField", "IntegerField", "BigIntegerField", "SmallIntegerField",
    "PositiveIntegerField", "PositiveBigIntegerField", "PositiveSmallIntegerField", "FloatField", "DecimalField",
    "BooleanField", "NullBooleanField", "CharField", "TextField", "EmailField", "URLField", "SlugField",
    "UUIDField", "DateField", "DateTimeField", "TimeField", "DurationField", "GenericIPAddressField",
})


def projected_fields(model: type[Model], grant: ModelMCPConfig) -> dict[str, Field]:
    policy = grant.read_policy
    if policy is None:
        raise ReadPolicyError()
    if model._meta.app_label in {"auth", "sessions"} or sensitive_name(model._meta.model_name) or "user" in model._meta.model_name.lower():
        raise ReadPolicyError()
    columns: dict[str, Field] = {}
    seen: set[str] = set()
    for name in policy.fields:
        try:
            field = model._meta.get_field(name)
        except Exception:
            raise ReadPolicyError() from None
        if not isinstance(field, Field):
            raise ReadPolicyError()
        if isinstance(field, (ForeignKey, OneToOneField)):
            target = field.target_field
        elif field.is_relation:
            raise ReadPolicyError()
        else:
            target = field
        if not field.concrete or field.many_to_many or target.get_internal_type() not in SCALAR_TYPES:
            raise ReadPolicyError()
        if field.name in grant.hidden_fields or field.attname in grant.hidden_fields or field.attname in seen:
            raise ReadPolicyError()
        if sensitive_name(field.name) or sensitive_name(field.attname):
            raise ReadPolicyError()
        seen.add(field.attname)
        columns[name] = field
    if not any(field.primary_key for field in columns.values()):
        raise ReadPolicyError("The scalar projection must include the primary key.")
    return columns


def scalar_value(value: object) -> Scalar:
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, (datetime, date, time)):
        value = value.isoformat()
    elif isinstance(value, (Decimal, UUID, timedelta)):
        value = str(value)
    if isinstance(value, str) and len(value) <= MAX_TEXT:
        return value
    raise ReadPolicyError("The model returned a value outside its scalar policy.")


def serialize_projected(objects: Iterable[Mapping[str, object]], columns: dict[str, Field]) -> list[dict[str, Scalar]]:
    return [{name: scalar_value(obj[field.attname]) for name, field in columns.items()} for obj in objects]


def schema_fields(model: type[Model], grant: ModelMCPConfig) -> dict[str, Field]:
    if grant.read_policy is not None:
        return projected_fields(model, grant)
    return {f.name: f for f in model._meta.fields if f.name not in grant.hidden_fields}
