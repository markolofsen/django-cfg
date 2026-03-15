"""
Typed DRF serializer base classes with proper validated_data narrowing.

Problem:
    Pyright infers `serializer.validated_data` as `Any` (or `empty | None` in strict mode)
    because DRF's `is_valid()` stub has no overload for `raise_exception=True`.
    Python's type system has no `TypeAssert` / `asserts` mechanism (unlike TypeScript),
    so we cannot narrow the type *after* a void exception-raising call.

Solution:
    Provide base serializer classes with `@overload` on `is_valid()` that:
    - `is_valid(raise_exception=True)` -> `Literal[True]`  (never False, never raises False)
    - `is_valid(raise_exception=False)` / `is_valid()` -> `bool`

    And `validated_data` typed as `dict[str, Any]` which is correct for
    `Serializer` (not `ListSerializer`) after successful validation.

Usage:
    from django_cfg.core.types.serializers import TypedSerializer, TypedModelSerializer

    class MySerializer(TypedSerializer):
        name = serializers.CharField()

    # In view:
    serializer = MySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    name = serializer.validated_data["name"]  # str, no type: ignore needed
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, overload

from rest_framework import serializers

if TYPE_CHECKING:
    pass


class TypedSerializer(serializers.Serializer):
    """
    Serializer base class with narrowed validated_data type.

    After `is_valid(raise_exception=True)`, Pyright knows:
    - The call returns `Literal[True]`
    - `validated_data` is `dict[str, Any]`

    This eliminates false positives on `.get()` and `[]` access.
    """

    @overload
    def is_valid(self, *, raise_exception: Literal[True]) -> Literal[True]: ...
    @overload
    def is_valid(self, *, raise_exception: Literal[False] = ...) -> bool: ...
    @overload
    def is_valid(self, *, raise_exception: bool = ...) -> bool: ...

    def is_valid(self, *, raise_exception: bool = False) -> bool:
        return super().is_valid(raise_exception=raise_exception)

    @property
    def validated_data(self) -> dict[str, Any]:
        return super().validated_data  # type: ignore[return-value]


class TypedModelSerializer(serializers.ModelSerializer):
    """
    ModelSerializer base class with narrowed validated_data type.

    Same benefits as TypedSerializer but for ModelSerializer.
    """

    @overload
    def is_valid(self, *, raise_exception: Literal[True]) -> Literal[True]: ...
    @overload
    def is_valid(self, *, raise_exception: Literal[False] = ...) -> bool: ...
    @overload
    def is_valid(self, *, raise_exception: bool = ...) -> bool: ...

    def is_valid(self, *, raise_exception: bool = False) -> bool:
        return super().is_valid(raise_exception=raise_exception)

    @property
    def validated_data(self) -> dict[str, Any]:
        return super().validated_data  # type: ignore[return-value]
