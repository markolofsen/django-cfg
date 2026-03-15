"""
Protocol definitions for ModelAdmin mixin compatibility.

Defines the contracts that mixins (ViewMixin, FlashMixin, PydanticAdminMixin)
expect from Django's ModelAdmin at runtime, enabling type checking and IDE support.
"""

from typing import Any, Optional, Protocol, runtime_checkable

from django.db import models
from django.http import HttpRequest


@runtime_checkable
class ModelAdminProtocol(Protocol):
    """
    Declares attributes and methods that Django's ModelAdmin provides.

    Used by ViewMixin and PydanticAdminMixin to declare what they expect
    from the ModelAdmin they are mixed into. Enables type checkers (mypy,
    pyright) to verify mixin method bodies against a known interface.
    """

    model: type[models.Model]
    readonly_fields: list[str]
    _current_request: Optional[HttpRequest]

    def get_object(
        self,
        request: HttpRequest,
        object_id: str,
        from_field: Optional[str] = None,
    ) -> Optional[models.Model]: ...

    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj: Optional[models.Model] = None,
    ) -> list[str]: ...

    def get_fieldsets(
        self,
        request: HttpRequest,
        obj: Optional[models.Model] = None,
    ) -> tuple[tuple[Optional[str], dict[str, Any]], ...]: ...

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: Optional[str] = None,
        form_url: str = "",
        extra_context: Optional[dict[str, Any]] = None,
    ) -> Any: ...

    def changelist_view(
        self,
        request: HttpRequest,
        extra_context: Optional[dict[str, Any]] = None,
    ) -> Any: ...

    def formfield_for_dbfield(
        self,
        db_field: Any,
        request: HttpRequest,
        **kwargs: Any,
    ) -> Any: ...


@runtime_checkable
class FlashMixinProtocol(Protocol):
    """
    Declares flash session methods expected by flash display methods.

    Ensures that any class using `create_flash_display_method()` has the
    required session management methods available.
    """

    def _flash_session_key(self, obj: models.Model, field_name: str) -> str: ...

    def _get_pending_flash_fields(
        self,
        request: HttpRequest,
        obj: models.Model,
    ) -> dict[str, dict[str, Any]]: ...

    def _consume_flash(
        self,
        request: HttpRequest,
        obj: models.Model,
        field_name: str,
    ) -> Optional[dict[str, Any]]: ...
