"""
Base Parser - Common parsing logic for OpenAPI → IR.

This module defines the abstract BaseParser class that contains shared logic
for converting OpenAPI specifications to IR, regardless of version.

Version-specific logic (nullable handling, etc.) is delegated to subclasses.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..ir import (
    DjangoGlobalMetadata,
    IRContext,
    IROperationObject,
    IRParameterObject,
    IRRequestBodyObject,
    IRResponseObject,
    IRSchemaObject,
    OpenAPIInfo,
)
from .models import (
    OpenAPISpec,
    OperationObject,
    ParameterObject,
    PathItemObject,
    ReferenceObject,
    RequestBodyObject,
    ResponseObject,
    SchemaObject,
)


class BaseParser(ABC):
    """
    Abstract base parser for OpenAPI → IR conversion.

    Subclasses implement version-specific logic:
    - OpenAPI30Parser: Handles nullable: true
    - OpenAPI31Parser: Handles type: ['string', 'null']
    """

    def __init__(self, spec: OpenAPISpec):
        """
        Initialize parser with OpenAPI spec.

        Args:
            spec: Validated OpenAPISpec object
        """
        self.spec = spec
        self._schema_cache: dict[str, IRSchemaObject] = {}
        self._inline_schemas: dict[str, IRSchemaObject] = {}  # For inline request/response schemas

    # ===== Main Parse Method =====

    def parse(self) -> IRContext:
        """
        Parse OpenAPI spec to IRContext.

        Returns:
            IRContext with all schemas and operations

        Raises:
            ValueError: If COMPONENT_SPLIT_REQUEST is not detected or schema name conflicts found
        """
        # CRITICAL: Validate schema names BEFORE parsing
        # This prevents generation from starting with invalid schemas
        self._validate_schema_names()

        # Parse metadata
        openapi_info = self._parse_openapi_info()
        django_metadata = self._parse_django_metadata()

        # Parse schemas
        schemas = self._parse_all_schemas()

        # Parse operations (may add inline schemas to self._inline_schemas)
        operations = self._parse_all_operations()

        # Merge inline schemas into main schemas dict
        schemas.update(self._inline_schemas)

        return IRContext(
            openapi_info=openapi_info,
            django_metadata=django_metadata,
            schemas=schemas,
            operations=operations,
        )

    # ===== Metadata Parsing =====

    def _parse_openapi_info(self) -> OpenAPIInfo:
        """Parse OpenAPI info to IR."""
        info = self.spec.info
        return OpenAPIInfo(
            version=self.spec.normalized_version,
            title=info.title,
            description=info.description,
            api_version=info.version,
            servers=self.spec.server_urls,
            contact_name=info.contact.name if info.contact else None,
            contact_email=info.contact.email if info.contact else None,
            license_name=info.license.name if info.license else None,
            license_url=info.license.url if info.license else None,
        )

    def _parse_django_metadata(self) -> DjangoGlobalMetadata:
        """
        Parse Django/drf-spectacular metadata.

        CRITICAL: This method VALIDATES Django settings, not detects from schema.
        For Read-Only APIs (e.g., shop with only GET endpoints), there may be
        no Request models in the schema. This is VALID if COMPONENT_SPLIT_REQUEST
        is True in Django settings.

        Returns:
            DjangoGlobalMetadata with validated settings

        Raises:
            ValueError: If COMPONENT_SPLIT_REQUEST is False in Django settings
        """
        # Try to get settings from Django
        has_split = self._get_django_spectacular_setting('COMPONENT_SPLIT_REQUEST')
        has_patch = self._get_django_spectacular_setting('COMPONENT_SPLIT_PATCH')

        # Fallback to detection if Django settings not available
        if has_split is None:
            has_split = self._detect_component_split_request()

        if has_patch is None:
            has_patch = self._detect_component_split_patch()

        # Get DRF authentication classes
        auth_classes = self._get_drf_authentication_classes()

        return DjangoGlobalMetadata(
            component_split_request=has_split if has_split is not None else False,
            component_split_patch=has_patch if has_patch is not None else False,
            oas_version=self.spec.normalized_version,
            default_authentication_classes=auth_classes,
        )

    def _get_django_spectacular_setting(self, setting_name: str) -> bool | None:
        """
        Get drf-spectacular setting from Django settings.

        Args:
            setting_name: Name of the SPECTACULAR_SETTINGS key

        Returns:
            Setting value, or None if not available
        """
        try:
            from django.conf import settings
            if not settings.configured:
                return None

            spectacular_settings = getattr(settings, 'SPECTACULAR_SETTINGS', {})
            return spectacular_settings.get(setting_name)
        except ImportError:
            # Django not available (standalone usage)
            return None
        except Exception:
            # Any other error
            return None

    def _get_drf_authentication_classes(self) -> list[str]:
        """
        Get DRF default authentication classes from Django settings.

        Returns:
            List of authentication class paths, or empty list if not available
        """
        try:
            from django.conf import settings
            if not settings.configured:
                return []

            rest_framework = getattr(settings, 'REST_FRAMEWORK', {})
            auth_classes = rest_framework.get('DEFAULT_AUTHENTICATION_CLASSES', [])

            # Ensure it's a list
            if isinstance(auth_classes, (list, tuple)):
                return list(auth_classes)
            return []
        except ImportError:
            # Django not available (standalone usage)
            return []
        except Exception:
            # Any other error
            return []

    def _detect_component_split_request(self) -> bool:
        """
        Detect if COMPONENT_SPLIT_REQUEST: True is used.

        Detection strategy:
        1. Look for schema pairs: User + UserRequest
        2. Look for schema pairs: Task + TaskRequest
        3. At least one pair must exist

        Returns:
            True if Request/Response split detected, False otherwise
        """
        if not self.spec.components or not self.spec.components.schemas:
            return False

        schema_names = set(self.spec.components.schemas.keys())

        # Check for Request suffix pattern
        for name in schema_names:
            if name.endswith("Request"):
                # Check if response model exists (without Request suffix)
                response_name = name[:-7]  # Remove "Request"
                if response_name in schema_names:
                    return True

        return False

    def _detect_component_split_patch(self) -> bool:
        """
        Detect if COMPONENT_SPLIT_PATCH: True is used.

        Detection strategy:
        1. Look for schema pairs: User + PatchedUser
        2. At least one pair must exist

        Returns:
            True if PATCH split detected
        """
        if not self.spec.components or not self.spec.components.schemas:
            return False

        schema_names = set(self.spec.components.schemas.keys())

        # Check for Patched prefix pattern
        for name in schema_names:
            if name.startswith("Patched"):
                # Check if base model exists (without Patched prefix)
                base_name = name[7:]  # Remove "Patched"
                if base_name in schema_names:
                    return True

        return False

    # ===== Schema Validation =====

    def _validate_schema_names(self) -> None:
        """
        Validate schema names for conflicts BEFORE parsing.

        This method checks for:
        1. Case-insensitive duplicates (e.g., "User" and "user")
        2. Exact duplicates (e.g., "GRPCServerInfo" from two different serializers)

        Raises:
            ValueError: If schema name conflicts are detected (hard exit with traceback)

        Example conflicts:
            - Case-insensitive: "Profile" and "profile" → filesystem conflict
            - Exact duplicate: "HealthCheck" from multiple serializers → schema conflict
        """
        import traceback
        import sys

        if not self.spec.components or not self.spec.components.schemas:
            return  # No schemas to validate

        schema_names = list(self.spec.components.schemas.keys())
        lowercase_map = {}
        exact_duplicate_sources = {}

        for name in schema_names:
            lowercase = name.lower()

            # Check case-insensitive duplicates
            if lowercase in lowercase_map:
                existing_name = lowercase_map[lowercase]
                error_msg = (
                    f"\n{'=' * 80}\n"
                    f"❌ SCHEMA NAME CONFLICT DETECTED\n"
                    f"{'=' * 80}\n\n"
                    f"Conflict Type: Case-insensitive duplicate\n"
                    f"Schema Names:\n"
                    f"  1. '{existing_name}'\n"
                    f"  2. '{name}'\n\n"
                    f"Problem:\n"
                    f"  These names differ only in casing and will cause conflicts on\n"
                    f"  case-insensitive filesystems (macOS, Windows).\n\n"
                    f"Solution:\n"
                    f"  Rename one of the Django serializers to make them distinct.\n"
                    f"  Example: {name}Serializer → {name}DetailSerializer\n\n"
                    f"{'=' * 80}\n"
                )

                # Print full error with traceback
                print(error_msg, file=sys.stderr)
                print("\n🔍 Traceback (schema validation):", file=sys.stderr)
                traceback.print_stack(file=sys.stderr)

                # Hard exit - stop generation immediately
                raise ValueError(
                    f"Case-insensitive schema name conflict: '{existing_name}' vs '{name}'. "
                    f"Cannot generate client with conflicting schema names."
                )

            lowercase_map[lowercase] = name

            # Track schema sources for exact duplicate detection
            schema = self.spec.components.schemas.get(name)
            if schema and not isinstance(schema, ReferenceObject):
                # Get source information from schema
                title = getattr(schema, 'title', name)
                description = getattr(schema, 'description', '')

                # Create signature for duplicate detection
                if name in exact_duplicate_sources:
                    # Found exact duplicate!
                    existing = exact_duplicate_sources[name]
                    error_msg = (
                        f"\n{'=' * 80}\n"
                        f"❌ SCHEMA NAME CONFLICT DETECTED\n"
                        f"{'=' * 80}\n\n"
                        f"Conflict Type: Exact duplicate schema name\n"
                        f"Schema Name: '{name}'\n\n"
                        f"Sources:\n"
                        f"  1. {existing['title']}\n"
                        f"     Description: {existing['description'][:100]}\n"
                        f"  2. {title}\n"
                        f"     Description: {description[:100]}\n\n"
                        f"Problem:\n"
                        f"  Multiple serializers are generating the same schema name '{name}'.\n"
                        f"  This causes schema conflicts in the generated API client and\n"
                        f"  OpenAPI documentation.\n\n"
                        f"Solution:\n"
                        f"  Rename one of the serializers to make them unique.\n"
                        f"  Examples:\n"
                        f"    - HealthCheckSerializer → GRPCHealthCheckSerializer\n"
                        f"    - ServerInfoSerializer → GRPCServerStatusSerializer\n\n"
                        f"{'=' * 80}\n"
                    )

                    # Print full error with traceback
                    print(error_msg, file=sys.stderr)
                    print("\n🔍 Traceback (schema validation):", file=sys.stderr)
                    traceback.print_stack(file=sys.stderr)

                    # Hard exit - stop generation immediately
                    raise ValueError(
                        f"Duplicate schema name detected: '{name}'. "
                        f"Multiple serializers are generating this schema. "
                        f"Cannot generate client with conflicting schemas."
                    )

                # Store for duplicate detection
                exact_duplicate_sources[name] = {
                    'title': title,
                    'description': description,
                }

    # ===== Schema Parsing =====

    def _parse_all_schemas(self) -> dict[str, IRSchemaObject]:
        """
        Parse all schemas from components.

        Note: Schema name validation is done in _validate_schema_names()
        which is called BEFORE this method in parse().
        """
        if not self.spec.components or not self.spec.components.schemas:
            return {}

        # Parse schemas (validation already done in _validate_schema_names)
        schemas = {}
        for name, schema_or_ref in self.spec.components.schemas.items():
            # Skip references for now
            if isinstance(schema_or_ref, ReferenceObject):
                continue

            schemas[name] = self._parse_schema(name, schema_or_ref)

        return schemas

    def _parse_schema(self, name: str, schema: SchemaObject) -> IRSchemaObject:
        """
        Parse SchemaObject to IRSchemaObject.

        Args:
            name: Schema name (e.g., 'User', 'UserRequest')
            schema: Raw SchemaObject from OpenAPI spec

        Returns:
            IRSchemaObject with Request/Response split awareness
        """
        # Check cache
        if name in self._schema_cache:
            return self._schema_cache[name]

        # Detect Request/Response/Patch model type
        is_request = name.endswith("Request")
        is_patch = name.startswith("Patched")
        is_response = not is_request and not is_patch

        # Determine related models
        related_request = None
        related_response = None

        if is_response:
            # Check if UserRequest exists
            potential_request = f"{name}Request"
            if self._schema_exists(potential_request):
                related_request = potential_request

        if is_request:
            # Extract base name (User from UserRequest)
            base_name = name[:-7]  # Remove "Request"
            if self._schema_exists(base_name):
                related_response = base_name

        if is_patch:
            # Extract base name (User from PatchedUser)
            base_name = name[7:]  # Remove "Patched"
            if self._schema_exists(base_name):
                related_response = base_name

        # Parse properties
        properties = {}
        if schema.properties:
            for prop_name, prop_schema_or_ref in schema.properties.items():
                if isinstance(prop_schema_or_ref, ReferenceObject):
                    # Resolve reference
                    properties[prop_name] = self._resolve_ref(prop_schema_or_ref)
                else:
                    # Handle allOf/anyOf/oneOf (common in drf-spectacular for enum fields)
                    ref_from_combinator = self._extract_ref_from_combinators(prop_schema_or_ref)
                    if ref_from_combinator:
                        # Found $ref in allOf/anyOf/oneOf - resolve it
                        resolved_schema = self._resolve_ref(ref_from_combinator)
                        # Preserve nullable attribute from parent schema
                        if self._detect_nullable(prop_schema_or_ref):
                            resolved_schema.nullable = True
                        properties[prop_name] = resolved_schema
                    else:
                        # No combinator $ref - parse normally
                        properties[prop_name] = self._parse_schema(
                            f"{name}.{prop_name}", prop_schema_or_ref
                        )

        # Parse array items
        items = None
        if schema.items:
            if isinstance(schema.items, ReferenceObject):
                # Resolve reference
                items = self._resolve_ref(schema.items)
            else:
                items = self._parse_schema(f"{name}.items", schema.items)

        # Parse additionalProperties (for Record<string, T> types)
        additional_properties = None
        if schema.additionalProperties and not isinstance(schema.additionalProperties, bool):
            if isinstance(schema.additionalProperties, ReferenceObject):
                # Resolve reference (e.g., Record<string, DatabaseConfig>)
                additional_properties = self._resolve_ref(schema.additionalProperties)
            else:
                additional_properties = self._parse_schema(
                    f"{name}.additionalProperties", schema.additionalProperties
                )
        elif schema.additionalProperties is True:
            # additionalProperties: true - allow any values
            additional_properties = IRSchemaObject(
                name=f"{name}.additionalProperties",
                type="any",
            )

        # Detect empty object {} (JSONField with no schema)
        # If type will be "object" but no properties and no additionalProperties,
        # treat as Record<string, any>
        normalized_type = self._normalize_type(schema)
        if (normalized_type == "object" and
            not properties and
            not additional_properties and
            schema.additionalProperties is not False):
            # Empty object {} - treat as Record<string, any>
            additional_properties = IRSchemaObject(
                name=f"{name}.additionalProperties",
                type="any",
            )

        # Create IR schema
        ir_schema = IRSchemaObject(
            name=name,
            type=normalized_type,
            format=schema.format,
            description=schema.description,
            nullable=self._detect_nullable(schema),
            properties=properties,
            required=schema.required or [],
            additional_properties=additional_properties,
            items=items,
            enum=schema.enum,
            enum_var_names=schema.x_enum_varnames,
            const=schema.const,
            is_request_model=is_request,
            is_response_model=is_response,
            is_patch_model=is_patch,
            related_request=related_request,
            related_response=related_response,
            min_length=schema.minLength,
            max_length=schema.maxLength,
            pattern=schema.pattern,
            minimum=schema.minimum,
            maximum=schema.maximum,
            read_only=schema.readOnly,
            write_only=schema.writeOnly,
            deprecated=schema.deprecated,
            default=schema.default,  # SMART DETECTION: Pass default value for JSONField(default=list) detection
        )

        # Cache
        self._schema_cache[name] = ir_schema

        return ir_schema

    def _schema_exists(self, name: str) -> bool:
        """Check if schema exists in components."""
        if not self.spec.components or not self.spec.components.schemas:
            return False
        return name in self.spec.components.schemas

    def _resolve_ref(self, ref: ReferenceObject) -> IRSchemaObject:
        """
        Resolve $ref to schema.

        Args:
            ref: ReferenceObject with $ref string

        Returns:
            IRSchemaObject (creates simple reference object)

        Example:
            {"$ref": "#/components/schemas/Profile"}
            → IRSchemaObject(name="Profile", type="object", ref="Profile")
        """
        # Extract schema name from $ref
        # Format: #/components/schemas/SchemaName
        if not ref.ref.startswith("#/components/schemas/"):
            raise ValueError(f"Unsupported $ref format: {ref.ref}")

        schema_name = ref.ref.split("/")[-1]

        # Create simple reference object
        # Parser will replace this with actual schema in generator
        return IRSchemaObject(
            name=schema_name,
            type="object",  # References are typically objects
            ref=schema_name,  # Store reference name
        )

    def _extract_ref_from_combinators(self, schema: SchemaObject) -> ReferenceObject | None:
        """
        Extract $ref from allOf/anyOf/oneOf combinators if present.

        DRF-spectacular often wraps enum references in allOf:
            "status": {
                "allOf": [{"$ref": "#/components/schemas/StatusEnum"}],
                "description": "...",
                "readOnly": true
            }

        This method extracts the $ref for resolution.

        Args:
            schema: SchemaObject that may contain allOf/anyOf/oneOf

        Returns:
            ReferenceObject if $ref found in combinators, None otherwise
        """
        # Check for allOf (most common in drf-spectacular for enum fields)
        if schema.allOf and len(schema.allOf) > 0:
            for item in schema.allOf:
                if isinstance(item, ReferenceObject):
                    return item

        # Check for anyOf
        if schema.anyOf and len(schema.anyOf) > 0:
            for item in schema.anyOf:
                if isinstance(item, ReferenceObject):
                    return item

        # Check for oneOf
        if schema.oneOf and len(schema.oneOf) > 0:
            for item in schema.oneOf:
                if isinstance(item, ReferenceObject):
                    return item

        # No combinators or no $ref found
        return None

    @abstractmethod
    def _detect_nullable(self, schema: SchemaObject) -> bool:
        """
        Detect if schema is nullable (version-specific).

        Subclasses implement:
        - OpenAPI30Parser: Check nullable: true
        - OpenAPI31Parser: Check type: ['string', 'null']

        Args:
            schema: Raw SchemaObject

        Returns:
            True if nullable, False otherwise
        """
        pass

    def _normalize_type(self, schema: SchemaObject) -> str:
        """
        Normalize schema type to single string.

        For OAS 3.1.0, type: ['string', 'null'] → 'string'

        Args:
            schema: Raw SchemaObject

        Returns:
            Normalized type string
        """
        if schema.base_type:
            return schema.base_type

        # Check anyOf: [{"type": "X"}, {"type": "null"}] pattern (Pydantic style)
        # Extract the actual type from anyOf if it's a simple nullable pattern
        if schema.anyOf and len(schema.anyOf) == 2:
            for item in schema.anyOf:
                if isinstance(item, SchemaObject) and item.base_type and item.base_type != 'null':
                    # Found the actual type (not null)
                    return item.base_type

        # Fallback: infer from other properties
        if schema.properties is not None:
            return "object"
        if schema.items is not None:
            return "array"

        # Special case: Empty object {} from Django JSONField(default=dict)
        # When drf-spectacular sees JSONField with no explicit type, it generates {}
        # This happens because Django models don't provide schema info for JSONField
        if (not schema.base_type and
            not schema.properties and
            not schema.items and
            not schema.anyOf and
            not schema.oneOf and
            not schema.allOf):
            # Empty schema {} - treat as object (most likely JSONField)
            return "object"

        # Special case: JSONField from Django has no type but description hints at dict/object
        # Check for keywords like: JSON, configuration, settings, config, dict
        if schema.description:
            desc_lower = schema.description.lower()
            if any(keyword in desc_lower for keyword in ['json', 'configuration', 'settings', 'config', 'dict']):
                return "object"

        return "string"  # Default

    # ===== Operation Parsing =====

    def _parse_all_operations(self) -> dict[str, IROperationObject]:
        """Parse all operations from paths."""
        if not self.spec.paths:
            return {}

        operations = {}
        for path, path_item in self.spec.paths.items():
            for method, operation in path_item.operations.items():
                if not operation.operationId:
                    # Generate operation_id if missing
                    operation.operationId = self._generate_operation_id(method, path)

                op_id = operation.operationId
                operations[op_id] = self._parse_operation(
                    operation, method, path, path_item
                )

        return operations

    def _parse_operation(
        self,
        operation: OperationObject,
        method: str,
        path: str,
        path_item: PathItemObject,
    ) -> IROperationObject:
        """Parse OperationObject to IROperationObject."""
        # Parse parameters
        parameters = self._parse_parameters(operation, path_item)

        # Parse request body
        request_body = None
        patch_request_body = None
        operation_id = operation.operationId or f"{method.lower()}_{path.replace('/', '_').strip('_')}"

        if operation.requestBody:
            if isinstance(operation.requestBody, ReferenceObject):
                # TODO: Resolve reference
                pass
            else:
                body = self._parse_request_body(operation.requestBody, operation_id)
                if method == "PATCH":
                    patch_request_body = body
                else:
                    request_body = body

        # Parse responses
        responses = self._parse_responses(operation.responses)

        return IROperationObject(
            operation_id=operation.operationId or "",
            http_method=method,
            path=path,
            summary=operation.summary,
            description=operation.description,
            tags=operation.tags or [],
            parameters=parameters,
            request_body=request_body,
            patch_request_body=patch_request_body,
            responses=responses,
            deprecated=operation.deprecated,
        )

    def _parse_parameters(
        self, operation: OperationObject, path_item: PathItemObject
    ) -> list[IRParameterObject]:
        """Parse parameters from operation and path item."""
        params = []

        # Path-level parameters
        if path_item.parameters:
            for param_or_ref in path_item.parameters:
                if isinstance(param_or_ref, ReferenceObject):
                    continue
                params.append(self._parse_parameter(param_or_ref))

        # Operation-level parameters
        if operation.parameters:
            for param_or_ref in operation.parameters:
                if isinstance(param_or_ref, ReferenceObject):
                    continue
                params.append(self._parse_parameter(param_or_ref))

        return params

    def _parse_parameter(self, param: ParameterObject) -> IRParameterObject:
        """Parse ParameterObject to IRParameterObject."""
        schema_type = "string"
        items_type = None

        if param.schema_:
            if isinstance(param.schema_, SchemaObject):
                schema_type = self._normalize_type(param.schema_)
                if schema_type == "array" and param.schema_.items:
                    if isinstance(param.schema_.items, SchemaObject):
                        items_type = self._normalize_type(param.schema_.items)

        return IRParameterObject(
            name=param.name,
            location=param.in_,
            schema_type=schema_type,
            required=param.required,
            description=param.description,
            default=param.example,  # Use example as default for now
            items_type=items_type,
            deprecated=param.deprecated,
        )

    def _parse_request_body(self, body: RequestBodyObject, operation_id: str) -> IRRequestBodyObject:
        """Parse RequestBodyObject to IRRequestBodyObject.

        Args:
            body: The request body object from OpenAPI spec
            operation_id: The operation ID for generating unique inline schema names
        """
        # Extract schema name from content
        schema_name = None
        content_type = "application/json"

        if body.content:
            for ct, media_type in body.content.items():
                content_type = ct
                if media_type.schema_:
                    if isinstance(media_type.schema_, ReferenceObject):
                        schema_name = media_type.schema_.ref_name
                    else:
                        # Inline schema - create unique name from operation_id
                        # Convert operation_id to PascalCase and add "Request" suffix
                        schema_name = self._to_pascal_case(operation_id) + "Request"

                        # Parse the inline schema and register it
                        inline_schema = self._parse_schema(schema_name, media_type.schema_)
                        inline_schema.is_request_model = True
                        self._inline_schemas[schema_name] = inline_schema
                break

        return IRRequestBodyObject(
            schema_name=schema_name or "UnknownRequest",
            content_type=content_type,
            required=body.required,
            description=body.description,
        )

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case or kebab-case to PascalCase."""
        from ..generator.proto.naming import to_pascal_case
        return to_pascal_case(name)

    def _parse_responses(
        self, responses: dict[str, ResponseObject | ReferenceObject]
    ) -> dict[int, IRResponseObject]:
        """Parse responses to IR."""
        ir_responses = {}

        for status_code_str, response_or_ref in responses.items():
            # Parse status code
            if status_code_str == "default":
                continue  # Skip default for now

            try:
                status_code = int(status_code_str)
            except ValueError:
                continue

            if isinstance(response_or_ref, ReferenceObject):
                # TODO: Resolve reference
                continue

            # Extract schema name and content type from content
            schema_name = None
            is_paginated = False
            content_type = "application/json"

            if response_or_ref.content:
                for ct, media_type in response_or_ref.content.items():
                    content_type = ct
                    if media_type.schema_:
                        if isinstance(media_type.schema_, ReferenceObject):
                            schema_name = media_type.schema_.ref_name
                            # Detect pagination
                            if "Paginated" in schema_name or "List" in schema_name:
                                is_paginated = True
                    break

            ir_responses[status_code] = IRResponseObject(
                status_code=status_code,
                schema_name=schema_name,
                content_type=content_type,
                description=response_or_ref.description,
                is_paginated=is_paginated,
            )

        return ir_responses

    def _generate_operation_id(self, method: str, path: str) -> str:
        """
        Generate operation_id from method and path.

        Examples:
            GET /api/users/ → users_list
            POST /api/users/ → users_create
            GET /api/users/{id}/ → users_retrieve
        """
        # Extract resource name from path
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        resource = parts[-1] if parts else "unknown"

        # Map method to action
        action_map = {
            "GET": "retrieve" if "{" in path else "list",
            "POST": "create",
            "PUT": "update",
            "PATCH": "partial_update",
            "DELETE": "destroy",
        }

        action = action_map.get(method, method.lower())

        return f"{resource}_{action}"
