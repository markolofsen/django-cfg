"""
Intermediate Representation (IR) models for Django-to-FastAPI conversion.

These models represent the parsed structure of Django models in a
framework-agnostic format that can be used by various generators.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class RelationType(str, Enum):
    """Type of relationship between models."""

    FOREIGN_KEY = "foreign_key"
    ONE_TO_ONE = "one_to_one"
    MANY_TO_MANY = "many_to_many"
    GENERIC_FOREIGN_KEY = "generic_foreign_key"


@dataclass
class ParsedField:
    """
    Represents a parsed Django model field.

    Contains all metadata needed to generate SQLModel/Pydantic fields.
    """

    # Basic info
    name: str
    django_type: str  # CharField, IntegerField, ForeignKey, etc.
    python_type: str  # str, int, Optional[int], etc.

    # Constraints
    max_length: Optional[int] = None
    nullable: bool = False
    blank: bool = False
    default: Optional[Any] = None
    primary_key: bool = False
    unique: bool = False
    db_index: bool = False
    editable: bool = True

    # Numeric constraints
    max_digits: Optional[int] = None
    decimal_places: Optional[int] = None

    # Choices
    choices: Optional[list[tuple[Any, str]]] = None

    # Relationship info (for FK, O2O, M2M)
    is_relation: bool = False
    related_model: Optional[str] = None  # Full path: "app_label.ModelName"
    related_model_name: Optional[str] = None  # Just model name
    related_table_name: Optional[str] = None  # Database table name (e.g., "profiles_customuser")
    relation_type: Optional[RelationType] = None
    on_delete: Optional[str] = None  # CASCADE, PROTECT, etc.
    related_name: Optional[str] = None
    through_model: Optional[str] = None  # For M2M with through
    related_pk_type: Optional[str] = None  # Primary key type of related model (UUIDField, BigAutoField, etc.)

    # PostgreSQL-specific
    is_array: bool = False
    array_base_type: Optional[str] = None
    is_json: bool = False

    # Auto timestamps
    auto_now: bool = False
    auto_now_add: bool = False

    # Metadata
    verbose_name: Optional[str] = None
    help_text: Optional[str] = None
    db_column: Optional[str] = None

    def get_sqlmodel_type(self, use_jsonb: bool = True) -> str:
        """Get SQLModel field type annotation."""
        base_type = self.python_type

        if self.nullable and not base_type.startswith("Optional"):
            return f"Optional[{base_type}]"
        return base_type

    def get_sqlmodel_field(self, use_jsonb: bool = True) -> str:
        """Generate SQLModel Field() definition."""
        parts = []

        # Default value
        if self.primary_key:
            parts.append("default=None")
            parts.append("primary_key=True")
        elif self.default is not None:
            if isinstance(self.default, str):
                parts.append(f'default="{self.default}"')
            elif callable(self.default):
                # Handle default factories
                parts.append("default_factory=dict" if self.is_json else f"default={self.default}")
            else:
                parts.append(f"default={self.default}")
        elif self.nullable:
            parts.append("default=None")

        # Constraints
        if self.max_length and not self.is_relation:
            parts.append(f"max_length={self.max_length}")
        if self.unique and not self.primary_key:
            parts.append("unique=True")
        if self.db_index and not self.primary_key and not self.unique:
            parts.append("index=True")

        # Foreign key
        if self.relation_type == RelationType.FOREIGN_KEY:
            table_name = self.related_table_name or (self.related_model_name.lower() if self.related_model_name else "unknown")
            parts.append(f'foreign_key="{table_name}.id"')

        # Description
        if self.help_text:
            escaped = self.help_text.replace('"', '\\"')
            parts.append(f'description="{escaped}"')

        if parts:
            return f"Field({', '.join(parts)})"
        return "Field()"


@dataclass
class ParsedRelationship:
    """Represents a relationship for SQLModel Relationship() definition."""

    name: str
    related_model: str
    relation_type: RelationType
    back_populates: Optional[str] = None
    sa_relationship_kwargs: Optional[dict] = None

    def get_type_hint(self) -> str:
        """Get type hint for relationship."""
        if self.relation_type == RelationType.MANY_TO_MANY:
            return f'list["{self.related_model}"]'
        return f'Optional["{self.related_model}"]'

    def get_relationship_def(self) -> str:
        """Generate Relationship() definition."""
        parts = []
        if self.back_populates:
            parts.append(f'back_populates="{self.back_populates}"')
        if self.sa_relationship_kwargs:
            for k, v in self.sa_relationship_kwargs.items():
                parts.append(f'{k}={v!r}')
        if parts:
            return f"Relationship({', '.join(parts)})"
        return "Relationship()"


@dataclass
class ParsedModel:
    """
    Represents a parsed Django model.

    Contains all fields, relationships, and metadata needed for generation.
    """

    # Basic info
    name: str
    app_label: str
    module_path: str  # Full Python path

    # Database
    table_name: str
    db_table_explicit: bool = False  # Was db_table set explicitly?

    # Fields
    fields: list[ParsedField] = field(default_factory=list)
    relationships: list[ParsedRelationship] = field(default_factory=list)

    # Meta options
    unique_together: list[tuple[str, ...]] = field(default_factory=list)
    index_together: list[tuple[str, ...]] = field(default_factory=list)
    indexes: list[dict] = field(default_factory=list)
    ordering: list[str] = field(default_factory=list)
    verbose_name: Optional[str] = None
    verbose_name_plural: Optional[str] = None
    abstract: bool = False

    # Inheritance
    parent_models: list[str] = field(default_factory=list)
    is_proxy: bool = False

    @property
    def full_name(self) -> str:
        """Get full model identifier."""
        return f"{self.app_label}.{self.name}"

    @property
    def pk_field(self) -> Optional[ParsedField]:
        """Get primary key field."""
        for f in self.fields:
            if f.primary_key:
                return f
        return None

    @property
    def regular_fields(self) -> list[ParsedField]:
        """Get non-relation fields."""
        return [f for f in self.fields if not f.is_relation]

    @property
    def relation_fields(self) -> list[ParsedField]:
        """Get only relation fields (FK, O2O)."""
        return [f for f in self.fields if f.is_relation]

    @property
    def foreign_keys(self) -> list[ParsedField]:
        """Get ForeignKey fields."""
        return [
            f for f in self.fields
            if f.relation_type == RelationType.FOREIGN_KEY
        ]

    @property
    def many_to_many(self) -> list[ParsedField]:
        """Get ManyToMany fields."""
        return [
            f for f in self.fields
            if f.relation_type == RelationType.MANY_TO_MANY
        ]


@dataclass
class GeneratedFile:
    """Represents a generated file."""

    path: Path
    content: str
    overwrite: bool = True

    @property
    def filename(self) -> str:
        return self.path.name


@dataclass
class GenerationResult:
    """Result of code generation."""

    models_count: int
    files: list[GeneratedFile]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def files_count(self) -> int:
        return len(self.files)
