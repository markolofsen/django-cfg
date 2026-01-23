"""
Django model introspector using runtime reflection.

Extracts model metadata from Django's model._meta API for accurate
field type detection and relationship mapping.
"""

import logging
from typing import Optional, Type

from django.apps import apps
from django.db import models

from ..ir.models import (
    ParsedField,
    ParsedModel,
    ParsedRelationship,
    RelationType,
)
from .type_mapper import TypeMapper, DJANGO_TO_PYTHON

logger = logging.getLogger(__name__)


class DjangoModelParser:
    """
    Parses Django models using runtime introspection.

    Uses Django's model._meta API to extract accurate field information,
    including relationships, constraints, and PostgreSQL-specific types.

    Example:
        parser = DjangoModelParser()
        models = parser.parse_apps(["users", "products"])
    """

    def __init__(
        self,
        type_mapper: Optional[TypeMapper] = None,
        exclude_models: Optional[list[str]] = None,
    ):
        self.type_mapper = type_mapper or TypeMapper()
        self.exclude_models = set(exclude_models or [])

    def parse_apps(
        self,
        app_labels: Optional[list[str]] = None,
        exclude_apps: Optional[list[str]] = None,
    ) -> list[ParsedModel]:
        """
        Parse all models from specified apps.

        Args:
            app_labels: Apps to parse (None = all apps)
            exclude_apps: Apps to exclude

        Returns:
            List of parsed models
        """
        exclude_apps = set(exclude_apps or [])
        parsed_models: list[ParsedModel] = []

        # Get app configs
        if app_labels:
            app_configs = [
                apps.get_app_config(label)
                for label in app_labels
                if label not in exclude_apps
            ]
        else:
            app_configs = [
                config for config in apps.get_app_configs()
                if config.label not in exclude_apps
            ]

        # Parse each app's models
        for app_config in app_configs:
            try:
                for model in app_config.get_models():
                    full_name = f"{app_config.label}.{model.__name__}"

                    # Skip excluded models
                    if full_name in self.exclude_models:
                        logger.debug(f"Skipping excluded model: {full_name}")
                        continue

                    # Skip abstract models
                    if model._meta.abstract:
                        logger.debug(f"Skipping abstract model: {full_name}")
                        continue

                    # Skip proxy models (they don't have their own table)
                    if model._meta.proxy:
                        logger.debug(f"Skipping proxy model: {full_name}")
                        continue

                    parsed = self.parse_model(model)
                    if parsed:
                        parsed_models.append(parsed)

            except Exception as e:
                logger.warning(f"Failed to parse app {app_config.label}: {e}")

        return parsed_models

    def parse_model(self, model: Type[models.Model]) -> Optional[ParsedModel]:
        """
        Parse a single Django model.

        Args:
            model: Django model class

        Returns:
            ParsedModel or None if parsing fails
        """
        try:
            meta = model._meta

            # Extract fields
            fields: list[ParsedField] = []
            relationships: list[ParsedRelationship] = []

            for field in meta.get_fields():
                parsed_field = self._parse_field(field)
                if parsed_field:
                    fields.append(parsed_field)

                    # Create relationship entries for FK/O2O
                    if parsed_field.is_relation and parsed_field.relation_type in (
                        RelationType.FOREIGN_KEY,
                        RelationType.ONE_TO_ONE,
                    ):
                        rel = self._create_relationship(parsed_field)
                        if rel:
                            relationships.append(rel)

            # Extract Meta options
            unique_together = self._get_unique_together(meta)
            index_together = self._get_index_together(meta)
            indexes = self._get_indexes(meta)
            ordering = list(meta.ordering) if meta.ordering else []

            return ParsedModel(
                name=model.__name__,
                app_label=meta.app_label,
                module_path=f"{model.__module__}.{model.__name__}",
                table_name=meta.db_table,
                db_table_explicit=bool(meta.db_table and meta.db_table != meta.db_table),
                fields=fields,
                relationships=relationships,
                unique_together=unique_together,
                index_together=index_together,
                indexes=indexes,
                ordering=ordering,
                verbose_name=str(meta.verbose_name) if meta.verbose_name else None,
                verbose_name_plural=str(meta.verbose_name_plural) if meta.verbose_name_plural else None,
                abstract=meta.abstract,
                parent_models=[p.__name__ for p in model.__mro__[1:] if hasattr(p, '_meta') and p != models.Model],
                is_proxy=meta.proxy,
            )

        except Exception as e:
            logger.error(f"Failed to parse model {model.__name__}: {e}")
            return None

    def _parse_field(self, field) -> Optional[ParsedField]:
        """Parse a Django field to ParsedField."""
        # Skip reverse relations (we'll handle them from the FK side)
        if hasattr(field, 'related_model') and not hasattr(field, 'attname'):
            # This is a reverse relation (like foo_set)
            return None

        # Skip auto-created fields that don't map to columns
        if getattr(field, 'auto_created', False) and not getattr(field, 'concrete', True):
            return None

        try:
            field_type = type(field).__name__

            # Basic field info
            parsed = ParsedField(
                name=getattr(field, 'name', str(field)),
                django_type=field_type,
                python_type=self._get_python_type(field),
                nullable=getattr(field, 'null', False),
                blank=getattr(field, 'blank', False),
                primary_key=getattr(field, 'primary_key', False),
                unique=getattr(field, 'unique', False),
                db_index=getattr(field, 'db_index', False),
                editable=getattr(field, 'editable', True),
                verbose_name=str(field.verbose_name) if hasattr(field, 'verbose_name') else None,
                help_text=str(field.help_text) if hasattr(field, 'help_text') and field.help_text else None,
                db_column=getattr(field, 'db_column', None),
            )

            # Max length
            if hasattr(field, 'max_length') and field.max_length:
                parsed.max_length = field.max_length

            # Decimal precision
            if field_type == 'DecimalField':
                parsed.max_digits = getattr(field, 'max_digits', None)
                parsed.decimal_places = getattr(field, 'decimal_places', None)

            # Choices
            if hasattr(field, 'choices') and field.choices:
                parsed.choices = list(field.choices)

            # Default value
            default = getattr(field, 'default', models.NOT_PROVIDED)
            if default is not models.NOT_PROVIDED:
                parsed.default = default

            # Auto timestamps (DateTimeField)
            parsed.auto_now = getattr(field, 'auto_now', False)
            parsed.auto_now_add = getattr(field, 'auto_now_add', False)

            # Handle relationships
            if isinstance(field, models.ForeignKey):
                parsed.is_relation = True
                parsed.relation_type = RelationType.FOREIGN_KEY
                parsed.related_model = f"{field.related_model._meta.app_label}.{field.related_model.__name__}"
                parsed.related_model_name = field.related_model.__name__
                parsed.related_table_name = field.related_model._meta.db_table
                parsed.on_delete = self._get_on_delete(field)
                parsed.related_name = getattr(field, 'related_name', None)
                # Get the primary key type of the related model
                related_pk = field.related_model._meta.pk
                if related_pk:
                    parsed.related_pk_type = type(related_pk).__name__
                # Update name to be the FK column name
                parsed.name = field.attname  # e.g., "user_id" instead of "user"

            elif isinstance(field, models.OneToOneField):
                parsed.is_relation = True
                parsed.relation_type = RelationType.ONE_TO_ONE
                parsed.related_model = f"{field.related_model._meta.app_label}.{field.related_model.__name__}"
                parsed.related_model_name = field.related_model.__name__
                parsed.related_table_name = field.related_model._meta.db_table
                parsed.on_delete = self._get_on_delete(field)
                parsed.related_name = getattr(field, 'related_name', None)
                # Get the primary key type of the related model
                related_pk = field.related_model._meta.pk
                if related_pk:
                    parsed.related_pk_type = type(related_pk).__name__
                parsed.name = field.attname

            elif isinstance(field, models.ManyToManyField):
                parsed.is_relation = True
                parsed.relation_type = RelationType.MANY_TO_MANY
                parsed.related_model = f"{field.related_model._meta.app_label}.{field.related_model.__name__}"
                parsed.related_model_name = field.related_model.__name__
                parsed.related_table_name = field.related_model._meta.db_table
                parsed.related_name = getattr(field, 'related_name', None)
                if hasattr(field, 'through') and field.through:
                    parsed.through_model = field.through.__name__

            # Handle PostgreSQL array fields
            if field_type == 'ArrayField':
                parsed.is_array = True
                base_field = getattr(field, 'base_field', None)
                if base_field:
                    parsed.array_base_type = type(base_field).__name__

            # Handle JSON field
            if field_type == 'JSONField':
                parsed.is_json = True

            return parsed

        except Exception as e:
            logger.debug(f"Failed to parse field {field}: {e}")
            return None

    def _get_python_type(self, field) -> str:
        """Get Python type for a field."""
        field_type = type(field).__name__

        # Get base type
        base_type = DJANGO_TO_PYTHON.get(field_type, "Any")

        # Handle nullable
        if getattr(field, 'null', False) and not base_type.startswith("Optional"):
            return f"Optional[{base_type}]"

        return base_type

    def _get_on_delete(self, field) -> str:
        """Get on_delete action name."""
        on_delete = getattr(field, 'remote_field', None)
        if on_delete and hasattr(on_delete, 'on_delete'):
            action = on_delete.on_delete
            return getattr(action, '__name__', 'CASCADE')
        return 'CASCADE'

    def _create_relationship(self, field: ParsedField) -> Optional[ParsedRelationship]:
        """Create a Relationship entry for SQLModel."""
        if not field.is_relation:
            return None

        # Create relationship name (remove _id suffix for relationship)
        rel_name = field.name
        if rel_name.endswith('_id'):
            rel_name = rel_name[:-3]

        return ParsedRelationship(
            name=rel_name,
            # Use full path (app_label.ModelName) to avoid conflicts with duplicate model names
            related_model=field.related_model or field.related_model_name or "Unknown",
            relation_type=field.relation_type or RelationType.FOREIGN_KEY,
            back_populates=field.related_name,
        )

    def _get_unique_together(self, meta) -> list[tuple[str, ...]]:
        """Extract unique_together constraints."""
        result = []
        if hasattr(meta, 'unique_together') and meta.unique_together:
            for constraint in meta.unique_together:
                if isinstance(constraint, (list, tuple)):
                    # Convert field names to column names
                    columns = tuple(self._field_to_column(meta, f) for f in constraint)
                    result.append(columns)
        return result

    def _get_index_together(self, meta) -> list[tuple[str, ...]]:
        """Extract index_together (deprecated but still used)."""
        result = []
        if hasattr(meta, 'index_together') and meta.index_together:
            for index in meta.index_together:
                if isinstance(index, (list, tuple)):
                    # Convert field names to column names
                    columns = tuple(self._field_to_column(meta, f) for f in index)
                    result.append(columns)
        return result

    def _field_to_column(self, meta, field_name: str) -> str:
        """Convert a field name to its actual column name."""
        try:
            field = meta.get_field(field_name)
            if hasattr(field, 'column'):
                return field.column
        except Exception:
            pass
        return field_name

    def _get_indexes(self, meta) -> list[dict]:
        """Extract model indexes."""
        result = []
        if hasattr(meta, 'indexes') and meta.indexes:
            for index in meta.indexes:
                # Convert field names to actual column names
                # For ForeignKey fields, column name is {field_name}_id
                fields = []
                for field_name in (index.fields if hasattr(index, 'fields') else []):
                    # Handle descending order prefix
                    is_desc = field_name.startswith('-')
                    clean_name = field_name.lstrip('-')

                    # Try to get the actual field to check if it's a ForeignKey
                    try:
                        field = meta.get_field(clean_name)
                        # ForeignKey/OneToOne fields have column attribute ending in _id
                        if hasattr(field, 'column'):
                            column_name = field.column
                        else:
                            column_name = clean_name
                    except Exception:
                        column_name = clean_name

                    # Preserve descending order prefix
                    if is_desc:
                        fields.append(f"-{column_name}")
                    else:
                        fields.append(column_name)

                result.append({
                    'name': getattr(index, 'name', None),
                    'fields': fields,
                    'unique': getattr(index, 'unique', False),
                })
        return result
