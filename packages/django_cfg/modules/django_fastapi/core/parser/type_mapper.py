"""
Type mapping system for Django to SQLModel/Pydantic conversion.

Maps Django field types to their Python type annotations and
SQLAlchemy column definitions.
"""

from typing import Any, Optional

from ..ir.models import ParsedField, RelationType


# Django field type -> Python type annotation
DJANGO_TO_PYTHON: dict[str, str] = {
    # Auto fields
    "AutoField": "int",
    "BigAutoField": "int",
    "SmallAutoField": "int",

    # String fields
    "CharField": "str",
    "TextField": "str",
    "SlugField": "str",
    "EmailField": "str",
    "URLField": "str",
    "FilePathField": "str",

    # Numeric fields
    "IntegerField": "int",
    "BigIntegerField": "int",
    "SmallIntegerField": "int",
    "PositiveIntegerField": "int",
    "PositiveBigIntegerField": "int",
    "PositiveSmallIntegerField": "int",
    "FloatField": "float",
    "DecimalField": "Decimal",

    # Boolean
    "BooleanField": "bool",
    "NullBooleanField": "Optional[bool]",

    # Date/Time
    "DateField": "date",
    "DateTimeField": "datetime",
    "TimeField": "time",
    "DurationField": "timedelta",

    # Binary/Files
    "BinaryField": "bytes",
    "FileField": "str",
    "ImageField": "str",

    # Special
    "UUIDField": "UUID",
    "JSONField": "dict[str, Any]",
    "GenericIPAddressField": "str",
    "IPAddressField": "str",

    # PostgreSQL specific (from django.contrib.postgres)
    "ArrayField": "list",
    "CICharField": "str",
    "CIEmailField": "str",
    "CITextField": "str",
    "HStoreField": "dict[str, str]",

    # Relations (ID column type)
    "ForeignKey": "int",
    "OneToOneField": "int",
    "ManyToManyField": "list[int]",
}

# Python types that need imports
PYTHON_TYPE_IMPORTS: dict[str, tuple[str, str]] = {
    "Decimal": ("decimal", "Decimal"),
    "date": ("datetime", "date"),
    "datetime": ("datetime", "datetime"),
    "time": ("datetime", "time"),
    "timedelta": ("datetime", "timedelta"),
    "UUID": ("uuid", "UUID"),
    "Any": ("typing", "Any"),
    "Optional": ("typing", "Optional"),
}

# SQLAlchemy column types for PostgreSQL-specific fields
SQLALCHEMY_COLUMN_TYPES: dict[str, str] = {
    "TextField": "Text",
    "JSONField": "JSONB",
    "ArrayField": "ARRAY",
    "HStoreField": "HSTORE",
    "UUIDField": "UUID",
    "DecimalField": "Numeric",
    "BinaryField": "LargeBinary",
    "GenericIPAddressField": "INET",
    "IPAddressField": "INET",
}


class TypeMapper:
    """
    Maps Django field types to Python/SQLModel types.

    Handles:
    - Basic type conversion
    - Nullable wrapping
    - PostgreSQL-specific types
    - Import collection
    """

    def __init__(
        self,
        use_jsonb: bool = True,
        use_array_fields: bool = True,
        use_uuid_type: bool = True,
    ):
        self.use_jsonb = use_jsonb
        self.use_array_fields = use_array_fields
        self.use_uuid_type = use_uuid_type
        self._imports: set[tuple[str, str]] = set()

    @property
    def imports(self) -> set[tuple[str, str]]:
        """Get collected imports as (module, name) tuples."""
        return self._imports

    def reset_imports(self) -> None:
        """Reset collected imports."""
        self._imports = set()

    def get_python_type(self, field: ParsedField) -> str:
        """
        Get Python type annotation for a Django field.

        Args:
            field: Parsed Django field

        Returns:
            Python type annotation string
        """
        django_type = field.django_type

        # Handle relation fields specially
        if field.is_relation:
            if field.relation_type == RelationType.MANY_TO_MANY:
                return f'list["{field.related_model_name}"]'
            # FK and O2O - return the ID type based on related model's PK
            if field.related_pk_type == "UUIDField":
                base_type = "UUID"
            elif field.related_pk_type in ("BigAutoField", "BigIntegerField"):
                base_type = "int"
            else:
                base_type = "int"  # Default to int for AutoField, etc.
        else:
            base_type = DJANGO_TO_PYTHON.get(django_type, "Any")

        # Handle array fields
        if field.is_array and field.array_base_type:
            inner_type = DJANGO_TO_PYTHON.get(field.array_base_type, "Any")
            self._collect_import(inner_type)
            base_type = f"list[{inner_type}]"

        # Collect imports for the base type
        self._collect_import(base_type)

        # Wrap nullable fields
        if field.nullable and not base_type.startswith("Optional"):
            self._imports.add(("typing", "Optional"))
            return f"Optional[{base_type}]"

        return base_type

    def get_fk_id_field_type(self, field: ParsedField) -> str:
        """Get type for FK ID field (e.g., user_id: Optional[UUID])."""
        # Determine base type from related model's PK
        if field.related_pk_type == "UUIDField":
            base_type = "UUID"
            self._imports.add(("uuid", "UUID"))
        else:
            base_type = "int"

        if field.nullable:
            self._imports.add(("typing", "Optional"))
            return f"Optional[{base_type}]"
        return base_type

    def _collect_import(self, type_str: str) -> None:
        """Collect required imports for a type."""
        # Extract base type from Optional[], list[], etc.
        base = type_str
        if base.startswith("Optional["):
            base = base[9:-1]
            self._imports.add(("typing", "Optional"))
        if base.startswith("list["):
            base = base[5:-1]
            self._imports.add(("typing", "List"))  # For older Python compat
        if base.startswith("dict["):
            self._imports.add(("typing", "Dict"))

        # Check if base type needs import
        if base in PYTHON_TYPE_IMPORTS:
            self._imports.add(PYTHON_TYPE_IMPORTS[base])

        # Handle Any
        if "Any" in type_str:
            self._imports.add(("typing", "Any"))

    def get_sqlalchemy_column(self, field: ParsedField) -> Optional[str]:
        """
        Get SQLAlchemy Column definition if needed.

        Returns None for simple types that don't need sa_column.
        """
        django_type = field.django_type

        # JSON field
        if django_type == "JSONField" and self.use_jsonb:
            self._imports.add(("sqlalchemy.dialects.postgresql", "JSONB"))
            return "Column(JSONB)"

        # Array field
        if field.is_array and self.use_array_fields:
            self._imports.add(("sqlalchemy.dialects.postgresql", "ARRAY"))
            base_sa_type = self._get_sa_type_for_array(field.array_base_type)
            return f"Column(ARRAY({base_sa_type}))"

        # Text field (for unlimited length)
        if django_type == "TextField":
            self._imports.add(("sqlalchemy", "Text"))
            return "Column(Text)"

        # Decimal field
        if django_type == "DecimalField":
            self._imports.add(("sqlalchemy", "Numeric"))
            precision = field.max_digits or 10
            scale = field.decimal_places or 2
            return f"Column(Numeric({precision}, {scale}))"

        # Binary field
        if django_type == "BinaryField":
            self._imports.add(("sqlalchemy", "LargeBinary"))
            return "Column(LargeBinary)"

        # UUID field with native PostgreSQL type
        # Use PGUUID alias to avoid conflict with Python's uuid.UUID
        if django_type == "UUIDField" and self.use_uuid_type:
            self._imports.add(("sqlalchemy.dialects.postgresql", "UUID as PGUUID"))
            return "Column(PGUUID(as_uuid=True))"

        # HStore field
        if django_type == "HStoreField":
            self._imports.add(("sqlalchemy.dialects.postgresql", "HSTORE"))
            return "Column(HSTORE)"

        # IP Address fields (GenericIPAddressField, IPAddressField)
        if django_type in ("GenericIPAddressField", "IPAddressField"):
            self._imports.add(("sqlalchemy.dialects.postgresql", "INET"))
            return "Column(INET)"

        # DateTimeField - use TIMESTAMP with timezone for Django's USE_TZ=True
        # This ensures timezone-aware datetimes work correctly with asyncpg
        if django_type == "DateTimeField":
            self._imports.add(("sqlalchemy", "DateTime"))
            return "Column(DateTime(timezone=True))"

        return None

    def _get_sa_type_for_array(self, base_type: Optional[str]) -> str:
        """Get SQLAlchemy type for array base type."""
        if not base_type:
            return "String"

        mapping = {
            "CharField": "String",
            "TextField": "Text",
            "IntegerField": "Integer",
            "BigIntegerField": "BigInteger",
            "FloatField": "Float",
            "BooleanField": "Boolean",
            "DateField": "Date",
            "DateTimeField": "DateTime",
            "UUIDField": "UUID",
        }

        sa_type = mapping.get(base_type, "String")

        # Add import for the type
        if sa_type in ("String", "Text", "Integer", "BigInteger", "Float", "Boolean", "Date", "DateTime"):
            self._imports.add(("sqlalchemy", sa_type))
        elif sa_type == "UUID":
            self._imports.add(("sqlalchemy.dialects.postgresql", "UUID"))

        return sa_type

    def get_default_value(self, field: ParsedField) -> Optional[str]:
        """Get default value representation for Field()."""
        if field.default is None:
            if field.nullable:
                return "None"
            return None

        default = field.default

        # Callable defaults
        if callable(default):
            func_name = getattr(default, "__name__", str(default))
            if func_name == "dict":
                return "default_factory=dict"
            if func_name == "list":
                return "default_factory=list"
            if "uuid" in func_name.lower():
                self._imports.add(("uuid", "uuid4"))
                return "default_factory=uuid4"
            if "now" in func_name.lower() or "today" in func_name.lower():
                return None  # Let SQLModel handle auto_now

        # String
        if isinstance(default, str):
            return f'"{default}"'

        # Boolean
        if isinstance(default, bool):
            return str(default)

        # Number
        if isinstance(default, (int, float)):
            return str(default)

        return None
