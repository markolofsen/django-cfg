"""
Smart Field Detection.

Infers field semantics from naming conventions and OpenAPI metadata.
Used to generate better form inputs, validation rules, and UI hints.

Usage:
    from django_cfg.modules.django_client.core.detection import detect_field_meta, FieldMeta
    from django_cfg.modules.django_client.core.types import FieldType

    meta = detect_field_meta("user_email", FieldType.STRING)
    # FieldMeta(input_type='email', validation='email', sensitive=False, readonly=False)

    meta = detect_field_meta("password", FieldType.STRING)
    # FieldMeta(input_type='password', validation=None, sensitive=True, readonly=False)

    meta = detect_field_meta("created_at", FieldType.STRING, format_type="date-time")
    # FieldMeta(input_type='datetime-local', validation=None, sensitive=False, readonly=True)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import FieldType, FormatType


class InputType(str, Enum):
    """HTML input types for form generation."""

    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    TEL = "tel"
    URL = "url"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    DATE = "date"
    TIME = "time"
    DATETIME_LOCAL = "datetime-local"
    TEXTAREA = "textarea"
    SELECT = "select"
    FILE = "file"
    HIDDEN = "hidden"
    COLOR = "color"


class ValidationRule(str, Enum):
    """Common validation rules."""

    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    UUID = "uuid"
    SLUG = "slug"
    IP_ADDRESS = "ip_address"
    CREDIT_CARD = "credit_card"
    POSTAL_CODE = "postal_code"


# =============================================================================
# Detection Patterns
# =============================================================================

# Field name patterns for email detection
EMAIL_PATTERNS = frozenset({"email", "e_mail", "mail", "email_address"})

# Field name patterns for phone detection
PHONE_PATTERNS = frozenset({"phone", "mobile", "cell", "telephone", "tel", "fax"})

# Field name patterns for password/secret detection
SENSITIVE_PATTERNS = frozenset({
    "password", "passwd", "pwd", "secret", "token", "api_key", "apikey",
    "private_key", "privatekey", "access_token", "refresh_token",
    "auth_token", "credential", "credentials",
})

# Field name patterns for URL detection
URL_PATTERNS = frozenset({
    "url", "uri", "link", "href", "website", "homepage", "webpage",
    "avatar_url", "image_url", "photo_url", "callback_url", "redirect_url",
})

# Field name patterns for readonly timestamp detection
TIMESTAMP_PATTERNS = frozenset({"created", "updated", "modified", "deleted"})
TIMESTAMP_SUFFIXES = ("_at", "_on", "_date", "_time", "_timestamp")

# Field name patterns for ID fields (readonly)
ID_PATTERNS = frozenset({"id", "pk", "uuid"})
ID_SUFFIXES = ("_id", "_pk", "_uuid")

# Field name patterns for slug fields
SLUG_PATTERNS = frozenset({"slug", "permalink", "handle"})

# Field name patterns for description/content (textarea)
TEXTAREA_PATTERNS = frozenset({
    "description", "content", "body", "text", "message", "comment",
    "bio", "biography", "about", "summary", "notes", "remarks",
})

# Field name patterns for color fields
COLOR_PATTERNS = frozenset({"color", "colour", "bgcolor", "background_color"})


# =============================================================================
# FieldMeta Dataclass
# =============================================================================


@dataclass(frozen=True, slots=True)
class FieldMeta:
    """
    Field metadata inferred from naming conventions.

    Attributes:
        input_type: HTML input type for form generation
        validation: Validation rule to apply (if any)
        sensitive: Whether field contains sensitive data (mask in logs/UI)
        readonly: Whether field should be readonly in forms
        placeholder: Suggested placeholder text
        autocomplete: HTML autocomplete attribute value
        pattern: Regex pattern for validation (HTML5 pattern attribute)
        min_length: Minimum length hint
        max_length: Maximum length hint
    """

    input_type: InputType = InputType.TEXT
    validation: ValidationRule | None = None
    sensitive: bool = False
    readonly: bool = False
    placeholder: str | None = None
    autocomplete: str | None = None
    pattern: str | None = None
    min_length: int | None = None
    max_length: int | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for template context."""
        return {
            "input_type": self.input_type.value,
            "validation": self.validation.value if self.validation else None,
            "sensitive": self.sensitive,
            "readonly": self.readonly,
            "placeholder": self.placeholder,
            "autocomplete": self.autocomplete,
            "pattern": self.pattern,
            "min_length": self.min_length,
            "max_length": self.max_length,
        }


# =============================================================================
# Detection Functions
# =============================================================================


def detect_field_meta(
    name: str,
    field_type: FieldType | str,
    *,
    format_type: FormatType | str | None = None,
    read_only: bool = False,
    write_only: bool = False,
) -> FieldMeta:
    """
    Infer field semantics from naming conventions.

    Args:
        name: Field name (e.g., "user_email", "created_at")
        field_type: OpenAPI field type
        format_type: OpenAPI format specifier (optional)
        read_only: Whether field is marked readOnly in schema
        write_only: Whether field is marked writeOnly in schema

    Returns:
        FieldMeta with inferred input type, validation, and hints

    Examples:
        >>> detect_field_meta("email", "string")
        FieldMeta(input_type=<InputType.EMAIL>, validation=<ValidationRule.EMAIL>, ...)

        >>> detect_field_meta("password", "string")
        FieldMeta(input_type=<InputType.PASSWORD>, sensitive=True, ...)

        >>> detect_field_meta("created_at", "string", format_type="date-time")
        FieldMeta(input_type=<InputType.DATETIME_LOCAL>, readonly=True, ...)
    """
    from ..types import FieldType as FT, FormatType as Fmt

    # Normalize inputs
    name_lower = name.lower()
    ft = FT(field_type) if isinstance(field_type, str) else field_type
    fmt = Fmt(format_type) if isinstance(format_type, str) and format_type else format_type

    # Check format-based detection first (most reliable)
    if fmt:
        meta = _detect_from_format(fmt, name_lower, read_only)
        if meta:
            return meta

    # Email detection
    if _matches_patterns(name_lower, EMAIL_PATTERNS):
        return FieldMeta(
            input_type=InputType.EMAIL,
            validation=ValidationRule.EMAIL,
            autocomplete="email",
            placeholder="user@example.com",
        )

    # Phone detection
    if _matches_patterns(name_lower, PHONE_PATTERNS):
        return FieldMeta(
            input_type=InputType.TEL,
            validation=ValidationRule.PHONE,
            autocomplete="tel",
            placeholder="+1 (555) 123-4567",
        )

    # Password/secret detection
    if _matches_patterns(name_lower, SENSITIVE_PATTERNS):
        autocomplete = "new-password" if "new" in name_lower else "current-password"
        return FieldMeta(
            input_type=InputType.PASSWORD,
            sensitive=True,
            autocomplete=autocomplete if "password" in name_lower else None,
            min_length=8,  # Common minimum password length
        )

    # URL detection
    if _matches_patterns(name_lower, URL_PATTERNS):
        return FieldMeta(
            input_type=InputType.URL,
            validation=ValidationRule.URL,
            autocomplete="url",
            placeholder="https://example.com",
        )

    # Timestamp detection (readonly)
    if _is_timestamp_field(name_lower) and ft == FT.STRING:
        return FieldMeta(
            input_type=InputType.DATETIME_LOCAL,
            readonly=True,
        )

    # ID field detection (readonly)
    if _is_id_field(name_lower):
        return FieldMeta(
            input_type=InputType.TEXT,
            readonly=True,
        )

    # Slug detection
    if _matches_patterns(name_lower, SLUG_PATTERNS):
        return FieldMeta(
            input_type=InputType.TEXT,
            validation=ValidationRule.SLUG,
            pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
            placeholder="my-slug-here",
        )

    # Textarea detection (long text fields)
    if _matches_patterns(name_lower, TEXTAREA_PATTERNS) and ft == FT.STRING:
        return FieldMeta(
            input_type=InputType.TEXTAREA,
        )

    # Color detection
    if _matches_patterns(name_lower, COLOR_PATTERNS):
        return FieldMeta(
            input_type=InputType.COLOR,
            pattern=r"^#[0-9A-Fa-f]{6}$",
            placeholder="#000000",
        )

    # Apply read_only from schema
    if read_only:
        return FieldMeta(
            input_type=get_default_input_type(ft, fmt),
            readonly=True,
        )

    # Default based on field type
    return FieldMeta(
        input_type=get_default_input_type(ft, fmt),
    )


def get_default_input_type(
    field_type: FieldType | str,
    format_type: FormatType | str | None = None,
) -> InputType:
    """
    Get default HTML input type for a field type.

    Args:
        field_type: OpenAPI field type
        format_type: OpenAPI format specifier (optional)

    Returns:
        InputType enum value
    """
    from ..types import FieldType as FT, FormatType as Fmt

    ft = FT(field_type) if isinstance(field_type, str) else field_type
    fmt = Fmt(format_type) if isinstance(format_type, str) and format_type else format_type

    # Format-based defaults
    if fmt:
        format_input_types = {
            Fmt.DATETIME: InputType.DATETIME_LOCAL,
            Fmt.DATE: InputType.DATE,
            Fmt.TIME: InputType.TIME,
            Fmt.EMAIL: InputType.EMAIL,
            Fmt.URI: InputType.URL,
            Fmt.URL: InputType.URL,
            Fmt.PASSWORD: InputType.PASSWORD,
            Fmt.BINARY: InputType.FILE,
        }
        if fmt in format_input_types:
            return format_input_types[fmt]

    # Type-based defaults
    type_input_types = {
        FT.STRING: InputType.TEXT,
        FT.INTEGER: InputType.NUMBER,
        FT.NUMBER: InputType.NUMBER,
        FT.BOOLEAN: InputType.CHECKBOX,
        FT.ARRAY: InputType.SELECT,
        FT.OBJECT: InputType.TEXTAREA,
    }

    return type_input_types.get(ft, InputType.TEXT)


# =============================================================================
# Helper Functions
# =============================================================================


def _matches_patterns(name: str, patterns: frozenset[str]) -> bool:
    """Check if name matches any pattern (exact or as component)."""
    # Exact match
    if name in patterns:
        return True

    # Component match (e.g., "user_email" contains "email")
    # Split by common separators
    parts = name.replace("-", "_").split("_")
    return any(part in patterns for part in parts)


def _is_timestamp_field(name: str) -> bool:
    """Check if field name indicates a timestamp."""
    # Exact match
    if name in TIMESTAMP_PATTERNS:
        return True

    # Suffix match
    return any(name.endswith(suffix) for suffix in TIMESTAMP_SUFFIXES)


def _is_id_field(name: str) -> bool:
    """Check if field name indicates an ID field."""
    # Exact match
    if name in ID_PATTERNS:
        return True

    # Suffix match
    return any(name.endswith(suffix) for suffix in ID_SUFFIXES)


def _detect_from_format(
    format_type: FormatType,
    name_lower: str,
    read_only: bool,
) -> FieldMeta | None:
    """Detect field meta from OpenAPI format."""
    from ..types import FormatType as Fmt

    if format_type == Fmt.EMAIL:
        return FieldMeta(
            input_type=InputType.EMAIL,
            validation=ValidationRule.EMAIL,
            autocomplete="email",
        )

    if format_type == Fmt.URI or format_type == Fmt.URL:
        return FieldMeta(
            input_type=InputType.URL,
            validation=ValidationRule.URL,
        )

    if format_type == Fmt.UUID:
        return FieldMeta(
            input_type=InputType.TEXT,
            validation=ValidationRule.UUID,
            readonly=read_only or _is_id_field(name_lower),
            pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        )

    if format_type == Fmt.DATETIME:
        is_timestamp = _is_timestamp_field(name_lower)
        return FieldMeta(
            input_type=InputType.DATETIME_LOCAL,
            readonly=read_only or is_timestamp,
        )

    if format_type == Fmt.DATE:
        return FieldMeta(
            input_type=InputType.DATE,
            readonly=read_only,
        )

    if format_type == Fmt.TIME:
        return FieldMeta(
            input_type=InputType.TIME,
            readonly=read_only,
        )

    if format_type == Fmt.PASSWORD:
        return FieldMeta(
            input_type=InputType.PASSWORD,
            sensitive=True,
            autocomplete="current-password",
        )

    if format_type == Fmt.BINARY:
        return FieldMeta(
            input_type=InputType.FILE,
        )

    if format_type == Fmt.IPV4 or format_type == Fmt.IPV6:
        return FieldMeta(
            input_type=InputType.TEXT,
            validation=ValidationRule.IP_ADDRESS,
        )

    return None
