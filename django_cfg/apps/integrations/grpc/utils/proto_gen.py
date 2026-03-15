"""
Proto file generation utilities.

Helps generate .proto files from Django models.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.apps import apps
from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


class ProtoFieldMapper:
    """
    Maps Django model fields to Protobuf types.

    Example:
        ```python
        mapper = ProtoFieldMapper()
        proto_type = mapper.get_proto_type(model_field)
        # 'string', 'int32', 'bool', etc.
        ```
    """

    # Django field -> Proto type mapping
    FIELD_TYPE_MAP = {
        models.CharField: "string",
        models.TextField: "string",
        models.EmailField: "string",
        models.URLField: "string",
        models.SlugField: "string",
        models.UUIDField: "string",
        models.IntegerField: "int32",
        models.BigIntegerField: "int64",
        models.SmallIntegerField: "int32",
        models.PositiveIntegerField: "uint32",
        models.PositiveBigIntegerField: "uint64",
        models.PositiveSmallIntegerField: "uint32",
        models.FloatField: "float",
        models.DecimalField: "string",  # Decimal as string to avoid precision loss
        models.BooleanField: "bool",
        models.DateField: "string",  # ISO 8601 date string
        models.DateTimeField: "string",  # ISO 8601 datetime string
        models.TimeField: "string",  # ISO 8601 time string
        models.DurationField: "string",  # Duration as string
        models.JSONField: "string",  # JSON as string
        models.BinaryField: "bytes",
        models.FileField: "string",  # File path/URL
        models.ImageField: "string",  # Image path/URL
    }

    def get_proto_type(self, field: models.Field) -> str:
        """
        Get Protobuf type for Django field.

        Args:
            field: Django model field

        Returns:
            Protobuf type string

        Example:
            >>> field = models.CharField(max_length=100)
            >>> mapper.get_proto_type(field)
            'string'
        """
        field_class = type(field)

        # Check for foreign key
        if isinstance(field, models.ForeignKey):
            return "int64"  # ID of related object

        # Check for many-to-many
        if isinstance(field, models.ManyToManyField):
            return "repeated int64"  # IDs of related objects

        # Check for one-to-one
        if isinstance(field, models.OneToOneField):
            return "int64"  # ID of related object

        # Check field type map
        for django_field_type, proto_type in self.FIELD_TYPE_MAP.items():
            if isinstance(field, django_field_type):
                return proto_type

        # Default to string
        logger.warning(f"Unknown field type {field_class.__name__}, defaulting to string")
        return "string"

    def is_repeated(self, field: models.Field) -> bool:
        """
        Check if field should be repeated in proto.

        Args:
            field: Django model field

        Returns:
            True if field should be repeated
        """
        return isinstance(field, models.ManyToManyField)

    def is_optional(self, field: models.Field) -> bool:
        """
        Check if field should be optional in proto.

        Args:
            field: Django model field

        Returns:
            True if field should be optional
        """
        return field.null or field.blank or hasattr(field, "default")


class ProtoGenerator:
    """
    Generates .proto files from Django models.

    Features:
    - Auto-generates message definitions
    - Handles field types
    - Supports relationships
    - Configurable naming conventions

    Example:
        ```python
        from myapp.models import User

        generator = ProtoGenerator()
        proto_content = generator.generate_message(User)

        # Write to file
        with open('user.proto', 'w') as f:
            f.write(proto_content)
        ```
    """

    def __init__(self, package_prefix: str = "", field_naming: str = "snake_case"):
        """
        Initialize proto generator.

        Args:
            package_prefix: Package prefix for proto files
            field_naming: Field naming convention ('snake_case' or 'camelCase')
        """
        self.package_prefix = package_prefix
        self.field_naming = field_naming
        self.mapper = ProtoFieldMapper()

    def generate_message(
        self,
        model: type,
        include_id: bool = True,
        include_timestamps: bool = True,
    ) -> str:
        """
        Generate protobuf message for Django model.

        Args:
            model: Django model class
            include_id: Include id field
            include_timestamps: Include created_at/updated_at fields

        Returns:
            Proto message definition string

        Example:
            >>> from myapp.models import User
            >>> generator = ProtoGenerator()
            >>> print(generator.generate_message(User))
            message User {
              int64 id = 1;
              string username = 2;
              string email = 3;
            }
        """
        message_name = model.__name__
        lines = [f"message {message_name} {{"]

        field_number = 1

        # Track fields to skip to avoid duplicates
        fields_to_skip = set()

        # If we'll add id separately, skip it in the field iteration
        if include_id:
            fields_to_skip.add('id')

        # If we'll add timestamps separately, skip them in the field iteration
        if include_timestamps:
            if hasattr(model, "created_at"):
                fields_to_skip.add('created_at')
            if hasattr(model, "updated_at"):
                fields_to_skip.add('updated_at')

        # Add id field first if requested
        if include_id:
            lines.append(f"  int64 id = {field_number};")
            field_number += 1

        # Add model fields
        for field in model._meta.get_fields():
            # Skip reverse relations
            if field.auto_created and not field.concrete:
                continue

            # Skip many-to-many for now (handle separately)
            if isinstance(field, models.ManyToManyField):
                continue

            # Skip fields that will be added separately to avoid duplicates
            if field.name in fields_to_skip:
                continue

            # Get field info
            field_name = self._format_field_name(field.name)
            proto_type = self.mapper.get_proto_type(field)
            is_optional = self.mapper.is_optional(field)

            # Build field definition
            if is_optional and not field.primary_key:
                field_def = f"  optional {proto_type} {field_name} = {field_number};"
            else:
                field_def = f"  {proto_type} {field_name} = {field_number};"

            lines.append(field_def)
            field_number += 1

        # Add timestamp fields last if requested
        if include_timestamps:
            if hasattr(model, "created_at"):
                lines.append(f"  optional string created_at = {field_number};")
                field_number += 1
            if hasattr(model, "updated_at"):
                lines.append(f"  optional string updated_at = {field_number};")
                field_number += 1

        lines.append("}")

        return "\n".join(lines)

    def generate_service(
        self,
        service_name: str,
        model: type,
        methods: Optional[List[str]] = None,
    ) -> str:
        """
        Generate protobuf service definition.

        Args:
            service_name: Service name
            model: Django model class
            methods: List of methods to include (default: CRUD)

        Returns:
            Proto service definition string

        Example:
            >>> from myapp.models import User
            >>> generator = ProtoGenerator()
            >>> print(generator.generate_service("UserService", User))
            service UserService {
              rpc Create(CreateUserRequest) returns (User);
              rpc Get(GetUserRequest) returns (User);
              rpc Update(UpdateUserRequest) returns (User);
              rpc Delete(DeleteUserRequest) returns (Empty);
              rpc List(ListUserRequest) returns (ListUserResponse);
            }
        """
        if methods is None:
            methods = ["Create", "Get", "Update", "Delete", "List"]

        model_name = model.__name__
        lines = [f"service {service_name} {{"]

        for method in methods:
            if method == "Create":
                lines.append(f"  rpc Create(Create{model_name}Request) returns ({model_name});")
            elif method == "Get":
                lines.append(f"  rpc Get(Get{model_name}Request) returns ({model_name});")
            elif method == "Update":
                lines.append(f"  rpc Update(Update{model_name}Request) returns ({model_name});")
            elif method == "Delete":
                lines.append(f"  rpc Delete(Delete{model_name}Request) returns (google.protobuf.Empty);")
            elif method == "List":
                lines.append(f"  rpc List(List{model_name}Request) returns (List{model_name}Response);")

        lines.append("}")

        return "\n".join(lines)

    def generate_proto_file(
        self,
        models_list: List[type],
        service_name: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        """
        Generate complete .proto file for models.

        Args:
            models_list: List of Django model classes
            service_name: Optional service name
            output_path: Optional output file path

        Returns:
            Complete proto file content

        Example:
            >>> from myapp.models import User, Post
            >>> generator = ProtoGenerator()
            >>> content = generator.generate_proto_file(
            ...     [User, Post],
            ...     service_name="MyAppService"
            ... )
        """
        lines = [
            'syntax = "proto3";',
            "",
        ]

        # Add package
        if self.package_prefix:
            lines.append(f"package {self.package_prefix};")
            lines.append("")

        # Add imports
        lines.append('import "google/protobuf/empty.proto";')
        lines.append("")

        # Add messages
        for model in models_list:
            message = self.generate_message(model)
            lines.append(message)
            lines.append("")

        # Add service if requested
        if service_name and models_list:
            service = self.generate_service(service_name, models_list[0])
            lines.append(service)
            lines.append("")

        content = "\n".join(lines)

        # Write to file if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content)
            logger.info(f"Generated proto file: {output_path}")

        return content

    def _format_field_name(self, name: str) -> str:
        """
        Format field name according to naming convention.

        Args:
            name: Original field name

        Returns:
            Formatted field name
        """
        if self.field_naming == "camelCase":
            parts = name.split("_")
            return parts[0] + "".join(p.capitalize() for p in parts[1:])
        else:
            # snake_case (default)
            return name


def generate_proto_for_app(app_label: str, output_dir: Optional[Path] = None) -> int:
    """
    Generate proto files for all models in an app.

    Args:
        app_label: Django app label
        output_dir: Output directory (default: protos/)

    Returns:
        Number of proto files generated

    Example:
        ```python
        from django_cfg.apps.integrations.grpc.utils.proto_gen import generate_proto_for_app

        count = generate_proto_for_app('myapp')
        print(f"Generated {count} proto file(s)")
        ```
    """
    # Get gRPC config from django-cfg (Pydantic)
    from ..services.management.config_helper import get_grpc_config

    grpc_config = get_grpc_config()
    proto_config = grpc_config.proto if grpc_config else None

    # Get output directory
    if output_dir is None:
        if proto_config:
            output_dir_str = proto_config.output_dir
        else:
            output_dir_str = "protos"  # Fallback

        output_dir = Path(output_dir_str)

        # Make absolute if relative
        if not output_dir.is_absolute():
            output_dir = settings.BASE_DIR / output_dir

    # Get app config
    try:
        app_config = apps.get_app_config(app_label)
    except LookupError:
        logger.error(f"App '{app_label}' not found")
        return 0

    # Get models
    models_list = [
        model for model in app_config.get_models()
        if not model._meta.abstract
    ]

    if not models_list:
        logger.warning(f"No models found in app '{app_label}'")
        return 0

    # Build package name: combine prefix + app_label
    if proto_config and proto_config.package_prefix:
        full_package = f"{proto_config.package_prefix}.{app_label}"
    else:
        full_package = app_label

    # Get field naming
    field_naming = proto_config.field_naming if proto_config else "snake_case"

    # Generate proto file
    generator = ProtoGenerator(
        package_prefix=full_package,
        field_naming=field_naming,
    )

    output_path = output_dir / f"{app_label}.proto"

    generator.generate_proto_file(
        models_list,
        service_name=f"{app_label.capitalize()}Service",
        output_path=output_path,
    )

    logger.info(f"Generated proto file for app '{app_label}' with {len(models_list)} model(s)")
    return 1


__all__ = [
    "ProtoFieldMapper",
    "ProtoGenerator",
    "generate_proto_for_app",
]
