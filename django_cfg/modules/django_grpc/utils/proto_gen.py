"""
Proto file generation utilities.

Helps generate .proto files from Django models.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.apps import apps
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
    - K-6: version_prefix for versioned package/service names

    Example — basic usage::

        from myapp.models import User

        generator = ProtoGenerator()
        proto_content = generator.generate_message(User)

        with open('user.proto', 'w') as f:
            f.write(proto_content)

    K-7 — Multi-version service registration pattern:

    When evolving a gRPC API, generate separate ``.proto`` files per version
    and register each servicer independently on the *same* ``grpc.aio.server``
    instance.  Both versions are reachable concurrently with no path conflicts
    because the full method path includes the service name::

        # v1: /myorg.users.v1.UserServiceV1/GetUser
        # v2: /myorg.users.v2.UserServiceV2/GetUser

    Implementation example::

        # protos/users_v1.proto (generated with version_prefix="v1")
        package myorg.users.v1;
        service UserServiceV1 { rpc GetUser(...) returns (...); }

        # protos/users_v2.proto (generated with version_prefix="v2")
        package myorg.users.v2;
        service UserServiceV2 { rpc GetUser(...) returns (...); }

        # In rungrpc / service discovery:
        users_v1_pb2_grpc.add_UserServiceV1Servicer_to_server(V1Servicer(), server)
        users_v2_pb2_grpc.add_UserServiceV2Servicer_to_server(V2Servicer(), server)

    Clients pin to a specific version by using the versioned stub class.
    Old clients keep working on V1; new clients use V2.  Decommission V1 by
    removing its servicer and bumping the ``min_version`` in the auth config
    once all clients have migrated.
    """

    def __init__(
        self,
        package_prefix: str = "",
        field_naming: str = "snake_case",
        version_prefix: str = "",
    ):
        """
        Initialize proto generator.

        Args:
            package_prefix: Package prefix for proto files (e.g. "myorg.myapp")
            field_naming: Field naming convention ('snake_case' or 'camelCase')
            version_prefix: K-6: API version segment injected into the proto package
                and service names (e.g. "v1" → package becomes "myorg.myapp.v1",
                service becomes "UserServiceV1"). Leave empty for unversioned output.

        Example — versioned package::

            gen = ProtoGenerator(
                package_prefix="myorg.users",
                version_prefix="v1",
            )
            # Generates: package myorg.users.v1;
            #            service UserServiceV1 { ... }
        """
        self.package_prefix = package_prefix
        self.field_naming = field_naming
        self.version_prefix = version_prefix  # K-6: e.g. "v1", "v2", ""
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
        # K-6: append version suffix to service name when version_prefix is set
        # (e.g. "UserService" → "UserServiceV1"). This follows the gRPC multi-version
        # registration convention: both services register independently under the same
        # proto package, distinguishable by name without path conflicts.
        versioned_service_name = (
            f"{service_name}{self.version_prefix.upper()}"
            if self.version_prefix
            else service_name
        )
        lines = [f"service {versioned_service_name} {{"]

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

        # K-6: build effective package name: prefix[.version]
        effective_package = self.package_prefix
        if self.version_prefix:
            effective_package = (
                f"{self.package_prefix}.{self.version_prefix}"
                if self.package_prefix
                else self.version_prefix
            )

        # Add package
        if effective_package:
            lines.append(f"package {effective_package};")
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
        from django_cfg.modules.django_grpc.utils.proto_gen import generate_proto_for_app

        count = generate_proto_for_app('myapp')
        print(f"Generated {count} proto file(s)")
        ```
    """
    # Get output directory
    # DjangoGrpcModuleConfig has no proto.output_dir field — use MEDIA_ROOT/protos
    if output_dir is None:
        from django_cfg.core.utils.paths import get_media_path
        output_dir = get_media_path("protos")

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
