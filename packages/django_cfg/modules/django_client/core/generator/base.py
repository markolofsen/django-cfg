"""
Base Generator - Common code generation logic.

This module defines the abstract BaseGenerator class that provides
common functionality for all code generators (Python, TypeScript, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ..ir import IRContext, IROperationObject, IRSchemaObject


class GeneratedFile:
    """
    Represents a generated file.

    Attributes:
        path: Relative file path (e.g., 'models.py', 'client.ts')
        content: Generated file content
        description: Human-readable description
    """

    def __init__(self, path: str, content: str, description: str | None = None):
        self.path = path
        self.content = content
        self.description = description

    def __repr__(self) -> str:
        return f"GeneratedFile(path={self.path!r}, size={len(self.content)} bytes)"


class BaseGenerator(ABC):
    """
    Abstract base generator for IR → Code conversion.

    Subclasses implement language-specific generation:
    - PythonGenerator: Generates Python client (Pydantic 2 + httpx)
    - TypeScriptGenerator: Generates TypeScript client (Fetch API)
    """

    def __init__(
        self,
        context: IRContext,
        client_structure: str = "namespaced",
        openapi_schema: dict | None = None,
        tag_prefix: str = "",
        package_config: dict | None = None,
        generate_package_files: bool = False,
        generate_zod_schemas: bool = False,
        generate_fetchers: bool = False,
        generate_swr_hooks: bool = False,
        group_name: str = "",
    ):
        """
        Initialize generator with IR context.

        Args:
            context: IRContext from parser
            client_structure: Client structure ("flat" or "namespaced")
            openapi_schema: OpenAPI schema dict (for embedding in client)
            tag_prefix: Prefix to add to all tag names (e.g., "cfg_")
            package_config: Package configuration (name, version, author, etc.)
            generate_package_files: Whether to generate package.json/pyproject.toml
            generate_zod_schemas: Whether to generate Zod schemas (TypeScript only)
            generate_fetchers: Whether to generate typed fetchers (TypeScript only)
            generate_swr_hooks: Whether to generate SWR hooks (TypeScript only, React)
            group_name: OpenAPI group name for regeneration command
        """
        self.context = context
        self.client_structure = client_structure
        self.openapi_schema = openapi_schema
        self.tag_prefix = tag_prefix
        self.package_config = package_config or {}
        self.generate_package_files = generate_package_files
        self.generate_zod_schemas = generate_zod_schemas
        self.generate_fetchers = generate_fetchers
        self.generate_swr_hooks = generate_swr_hooks
        self.group_name = group_name

    # ===== Namespaced Structure Helpers =====

    def group_operations_by_tag(self) -> dict[str, list[IROperationObject]]:
        """
        Group operations by their first tag with case-insensitive normalization.

        Tags are normalized to prevent duplicates caused by case differences
        (e.g., "Profiles" and "profiles" are treated as the same tag).
        The canonical tag (first encountered) is preserved for display purposes.

        Returns:
            Dictionary mapping canonical tag names to lists of operations.
            Operations without tags are grouped under "default".

        Examples:
            >>> ops = generator.group_operations_by_tag()
            >>> ops["users"]  # [list_op, create_op, retrieve_op, ...]
            >>> # "Users" and "users" are merged into one group with canonical "Users"
        """
        from collections import defaultdict

        ops_by_tag = defaultdict(list)
        tag_canonical = {}  # normalized_tag -> canonical_tag mapping
        tag_variants = defaultdict(set)  # Track all variants for warnings

        for op_id, operation in self.context.operations.items():
            tag = operation.tags[0] if operation.tags else "default"

            # Normalize tag to lowercase for comparison
            normalized_tag = tag.lower()

            # Track all case variants
            tag_variants[normalized_tag].add(tag)

            # Use first encountered version as canonical
            if normalized_tag not in tag_canonical:
                tag_canonical[normalized_tag] = tag

            # Group under canonical tag
            canonical = tag_canonical[normalized_tag]
            ops_by_tag[canonical].append(operation)

        # Warn about case inconsistencies
        for normalized, variants in tag_variants.items():
            if len(variants) > 1:
                canonical = tag_canonical[normalized]
                other_variants = sorted(variants - {canonical})
                print(f"⚠️  Warning: Found case variants of tag '{canonical}': {other_variants}")
                print(f"    → Using '{canonical}' as canonical tag")

        return dict(ops_by_tag)

    def tag_to_class_name(self, tag: str, suffix: str = "API") -> str:
        """
        Convert tag to PascalCase class name.

        Args:
            tag: Tag name (e.g., "users", "user-management", "django_cfg.auth")
            suffix: Class name suffix (default: "API")

        Returns:
            PascalCase class name with suffix and optional prefix

        Examples:
            >>> generator.tag_to_class_name("users")
            'UsersAPI'
            >>> generator.tag_to_class_name("user-management")
            'UserManagementAPI'
            >>> generator.tag_to_class_name("django_cfg.auth")
            'DjangoCfgAuthAPI'
            >>> generator = BaseGenerator(context, tag_prefix="cfg_")
            >>> generator.tag_to_class_name("auth")
            'CfgAuthAPI'
        """
        # Use tag_to_property_name to get normalized name with prefix
        normalized = self.tag_to_property_name(tag)
        # Split into words and capitalize
        words = normalized.split('_')
        return ''.join(word.capitalize() for word in words if word) + suffix

    def tag_to_property_name(self, tag: str) -> str:
        """
        Convert tag to valid property/variable name.

        Args:
            tag: Tag name (e.g., "Blog - Categories", "user-management", "django_cfg.leads")

        Returns:
            Valid identifier (snake_case for Python, camelCase for TS) with optional prefix

        Examples:
            >>> generator.tag_to_property_name("Blog - Categories")
            'blog_categories'
            >>> generator.tag_to_property_name("user-management")
            'user_management'
            >>> generator = BaseGenerator(context, tag_prefix="cfg_")
            >>> generator.tag_to_property_name("auth")
            'cfg_auth'
            >>> generator.tag_to_property_name("django_cfg.leads")
            'cfg_leads'  # django_cfg prefix is stripped before adding group prefix
        """
        from django.utils.text import slugify
        normalized = slugify(tag).replace('-', '_')

        # Strip common app label prefixes to avoid duplication
        # (e.g., "django_cfg_leads" → "leads" before adding group prefix)
        prefixes_to_strip = ['django_cfg_', 'django_cfg.']
        for prefix in prefixes_to_strip:
            prefix_normalized = slugify(prefix).replace('-', '_')
            if normalized.startswith(prefix_normalized):
                normalized = normalized[len(prefix_normalized):]
                break

        # Strip leading underscores after prefix removal
        # (e.g., "django_cfg.accounts" → "django_cfg_accounts" → "_accounts" → "accounts")
        normalized = normalized.lstrip('_')

        # Add group prefix if configured and not already present
        if self.tag_prefix:
            # Check if tag already starts with prefix (avoid duplication)
            if not normalized.startswith(self.tag_prefix):
                normalized = f"{self.tag_prefix}{normalized}"

        return normalized

    def extract_app_from_path(self, path: str) -> str | None:
        """
        Extract Django app name from URL path.

        Args:
            path: URL path (e.g., "/django_cfg_leads/leads/", "/django_cfg_newsletter/campaigns/", "/cfg/accounts/otp/")

        Returns:
            App name without trailing slash, or None if no app detected

        Examples:
            >>> generator.extract_app_from_path("/django_cfg_leads/leads/")
            'django_cfg_leads'
            >>> generator.extract_app_from_path("/django_cfg_newsletter/campaigns/")
            'django_cfg_newsletter'
            >>> generator.extract_app_from_path("/api/users/")
            'api'
            >>> generator.extract_app_from_path("/cfg/accounts/otp/")
            'accounts'
        """
        # Remove leading/trailing slashes and split
        parts = path.strip('/').split('/')

        # For cfg group URLs (/cfg/accounts/, /cfg/support/), skip the 'cfg' prefix
        if len(parts) >= 2 and parts[0] == 'cfg':
            return parts[1]

        # First part is usually the app name
        if parts:
            return parts[0]

        return None

    def tag_and_app_to_folder_name(self, tag: str, operations: list) -> str:
        """
        Generate folder name from tag and app name with smart deduplication.

        When tag matches app name, the redundant tag portion is omitted to avoid
        folder names like 'cfg__tasks__tasks'. This keeps naming clean and intuitive.

        Args:
            tag: Tag name (e.g., "Campaigns", "Tasks", "django_cfg.leads")
            operations: List of operations to extract app name from

        Returns:
            Folder name in one of these formats:
            - group__app__tag (when tag differs from app)
            - group__app (when tag matches app)
            - group (when all three match - rare case)

        Examples:
            >>> # Distinct tag and app
            >>> # operations with path="/django_cfg_newsletter/campaigns/"
            >>> generator.tag_and_app_to_folder_name("Campaigns", operations)
            'cfg__newsletter__campaigns'

            >>> # Tag matches app (deduplication applied)
            >>> # operations with path="/tasks/api/..."
            >>> generator.tag_and_app_to_folder_name("Tasks", operations)
            'cfg__tasks'

            >>> # Tag matches app (deduplication applied)
            >>> # operations with path="/django_cfg_leads/leads/"
            >>> generator.tag_and_app_to_folder_name("Leads", operations)
            'cfg__leads'

            >>> # Triple match - all same (rare)
            >>> # operations with path="/profiles/profiles/"
            >>> generator.tag_and_app_to_folder_name("Profiles", operations)  # group=profiles
            'profiles'
        """
        from django.utils.text import slugify

        # Extract app name from first operation's path
        app_name = None
        if operations:
            app_name = self.extract_app_from_path(operations[0].path)

        if not app_name:
            # Fallback: just use normalized tag
            return self.tag_to_property_name(tag)

        # Normalize app name (strip django_cfg prefix)
        normalized_app = slugify(app_name).replace('-', '_')
        prefixes_to_strip = ['django_cfg_', 'django_cfg.']
        for prefix in prefixes_to_strip:
            prefix_normalized = slugify(prefix).replace('-', '_')
            if normalized_app.startswith(prefix_normalized):
                normalized_app = normalized_app[len(prefix_normalized):]
                break
        normalized_app = normalized_app.lstrip('_')

        # Normalize tag (strip django_cfg prefix)
        normalized_tag = slugify(tag).replace('-', '_')
        for prefix in prefixes_to_strip:
            prefix_normalized = slugify(prefix).replace('-', '_')
            if normalized_tag.startswith(prefix_normalized):
                normalized_tag = normalized_tag[len(prefix_normalized):]
                break
        normalized_tag = normalized_tag.lstrip('_')

        # Smart deduplication: if tag matches app, skip tag portion
        if normalized_tag == normalized_app:
            # Tag is redundant with app name
            if self.tag_prefix:
                group = self.tag_prefix.rstrip('_')
                # Check if group also matches app (triple redundancy)
                if group == normalized_app:
                    # All three are the same, just use group
                    return group
                else:
                    # Tag matches app but not group: use group__app
                    return f"{group}__{normalized_app}"
            else:
                # No group prefix, just use app name
                return normalized_app

        # Build folder name: group__app__tag (when tag is distinct)
        if self.tag_prefix:
            # tag_prefix already has trailing underscore: "cfg_"
            group = self.tag_prefix.rstrip('_')
            return f"{group}__{normalized_app}__{normalized_tag}"
        else:
            return f"{normalized_app}__{normalized_tag}"

    def tag_to_display_name(self, tag: str) -> str:
        """
        Convert tag to human-readable display name for docstrings.

        This method strips common prefixes and formats the tag for display in
        documentation without adding group prefixes.

        Args:
            tag: Tag name (e.g., "django_cfg.leads", "Campaigns", "User Profile")

        Returns:
            Human-readable tag name (title case)

        Examples:
            >>> generator.tag_to_display_name("Campaigns")
            'Campaigns'
            >>> generator.tag_to_display_name("django_cfg.leads")
            'Leads'
            >>> generator.tag_to_display_name("django_cfg_accounts")
            'Accounts'
            >>> generator.tag_to_display_name("user-management")
            'User Management'
        """
        from django.utils.text import slugify

        # If tag is already in title case with spaces, return as-is
        if ' ' in tag and tag[0].isupper():
            return tag

        # Normalize the tag
        normalized = slugify(tag).replace('-', '_')

        # Strip common app label prefixes
        prefixes_to_strip = ['django_cfg_', 'django_cfg.']
        for prefix in prefixes_to_strip:
            prefix_normalized = slugify(prefix).replace('-', '_')
            if normalized.startswith(prefix_normalized):
                normalized = normalized[len(prefix_normalized):]
                break

        # Strip leading underscores
        normalized = normalized.lstrip('_')

        # Convert to title case with spaces
        words = normalized.split('_')
        return ' '.join(word.capitalize() for word in words if word)

    def remove_tag_prefix(self, operation_id: str, tag: str) -> str:
        """
        Remove tag prefix from operation_id.

        This method handles complex operation ID patterns by:
        1. Stripping common app label prefixes (django_cfg_*, etc.)
        2. Attempting to strip the normalized tag name
        3. Returning the cleaned operation_id

        Args:
            operation_id: Operation ID (e.g., "django_cfg_newsletter_campaigns_list", "posts_list")
            tag: Tag name (e.g., "Campaigns", "posts", "django_cfg.accounts")

        Returns:
            Operation ID without tag prefix

        Examples:
            >>> generator.remove_tag_prefix("posts_list", "posts")
            'list'
            >>> generator.remove_tag_prefix("django_cfg_newsletter_campaigns_list", "Campaigns")
            'list'
            >>> generator.remove_tag_prefix("django_cfg_accounts_token_refresh_create", "Auth")
            'token_refresh_create'
            >>> generator.remove_tag_prefix("retrieve", "users")
            'retrieve'  # No prefix to remove
        """
        import re

        from django.utils.text import slugify

        # First, strip common app label prefixes from operation_id
        # This handles cases like "django_cfg_newsletter_campaigns_list" or "cfg_support_tickets_list"
        # Remove only the cfg/django_cfg prefix, not the entire app name
        # Examples:
        #   cfg_support_tickets_list → support_tickets_list
        #   django_cfg_accounts_otp_request → accounts_otp_request
        cleaned_op_id = re.sub(r'^(django_)?cfg_', '', operation_id)

        # Now try to remove the normalized tag as a prefix
        # Normalize tag same way as tag_to_property_name but without adding group prefix
        normalized_tag = slugify(tag).replace('-', '_')

        # Strip django_cfg prefix from tag too
        tag_prefixes = ['django_cfg_', 'django_cfg.']
        for prefix in tag_prefixes:
            prefix_normalized = slugify(prefix).replace('-', '_')
            if normalized_tag.startswith(prefix_normalized):
                normalized_tag = normalized_tag[len(prefix_normalized):]
                break

        # Strip leading underscores from tag
        normalized_tag = normalized_tag.lstrip('_')

        # Remove tag prefix from operation_id if it matches
        # This ensures methods in each API folder have clean, contextual names
        # e.g., in cfg__support: "support_tickets_list" → "tickets_list"
        # e.g., in cfg__accounts: "accounts_otp_request" → "otp_request"
        tag_prefix = f"{normalized_tag}_"
        if cleaned_op_id.startswith(tag_prefix):
            cleaned_op_id = cleaned_op_id[len(tag_prefix):]

        return cleaned_op_id

    # ===== Main Generate Method =====

    @abstractmethod
    def generate(self) -> list[GeneratedFile]:
        """
        Generate all client files.

        Returns:
            List of GeneratedFile objects

        Examples:
            >>> generator = PythonGenerator(context)
            >>> files = generator.generate()
            >>> for file in files:
            ...     print(f"{file.path}: {len(file.content)} bytes")
            models.py: 1234 bytes
            client.py: 5678 bytes
        """
        pass

    # ===== Schema Generation (Abstract) =====

    @abstractmethod
    def generate_schema(self, schema: IRSchemaObject) -> str:
        """
        Generate code for a single schema.

        Args:
            schema: IRSchemaObject to generate

        Returns:
            Generated code (class definition, interface, etc.)

        Examples:
            >>> schema = IRSchemaObject(name="User", type="object", ...)
            >>> code = generator.generate_schema(schema)
            >>> # Python: "class User(BaseModel): ..."
            >>> # TypeScript: "interface User { ... }"
        """
        pass

    @abstractmethod
    def generate_enum(self, schema: IRSchemaObject) -> str:
        """
        Generate enum code from schema with x-enum-varnames.

        Args:
            schema: IRSchemaObject with enum + enum_var_names

        Returns:
            Generated enum code

        Examples:
            >>> schema = IRSchemaObject(
            ...     name="StatusEnum",
            ...     type="integer",
            ...     enum=[1, 2, 3],
            ...     enum_var_names=["STATUS_NEW", "STATUS_IN_PROGRESS", "STATUS_COMPLETE"]
            ... )
            >>> code = generator.generate_enum(schema)
            >>> # Python: "class StatusEnum(IntEnum): ..."
            >>> # TypeScript: "enum StatusEnum { ... }"
        """
        pass

    # ===== Operation Generation (Abstract) =====

    @abstractmethod
    def generate_operation(self, operation: IROperationObject) -> str:
        """
        Generate code for a single operation (endpoint method).

        Args:
            operation: IROperationObject to generate

        Returns:
            Generated method code

        Examples:
            >>> operation = IROperationObject(
            ...     operation_id="users_list",
            ...     http_method="GET",
            ...     path="/api/users/",
            ...     ...
            ... )
            >>> code = generator.generate_operation(operation)
            >>> # Python: "async def users_list(self, ...) -> list[User]: ..."
            >>> # TypeScript: "async usersList(...): Promise<User[]> { ... }"
        """
        pass

    # ===== Helpers =====

    def get_request_schemas(self) -> dict[str, IRSchemaObject]:
        """Get all request schemas (UserRequest, etc.)."""
        return self.context.request_models

    def get_response_schemas(self) -> dict[str, IRSchemaObject]:
        """Get all response schemas (User, etc.)."""
        return self.context.response_models

    def get_patch_schemas(self) -> dict[str, IRSchemaObject]:
        """Get all PATCH schemas (PatchedUser, etc.)."""
        return self.context.patch_models

    def get_enum_schemas(self) -> dict[str, IRSchemaObject]:
        """Get all enum schemas with x-enum-varnames."""
        return self.context.enum_schemas

    def _collect_enums_from_schemas(
        self, schemas: dict[str, IRSchemaObject]
    ) -> dict[str, IRSchemaObject]:
        """
        Recursively collect all enum schemas used by given schemas.

        This method extracts enums from:
        - Top-level enum schemas (StatusEnum as a component)
        - Nested enum properties (User.status where status has enum)
        - Array items with enums (Task.tags where tags[0] is enum)

        Auto-generates enum_var_names if not present:
        - "open" → "OPEN"
        - "waiting_for_user" → "WAITING_FOR_USER"

        Args:
            schemas: Dictionary of schemas to scan

        Returns:
            Dictionary of enum schemas found (with auto-generated var names)

        Examples:
            >>> schemas = {
            ...     "Payment": IRSchemaObject(
            ...         name="Payment",
            ...         type="object",
            ...         properties={
            ...             "status": IRSchemaObject(
            ...                 name="StatusEnum",
            ...                 type="string",
            ...                 enum=["open", "closed"]
            ...             )
            ...         }
            ...     )
            ... }
            >>> enums = generator._collect_enums_from_schemas(schemas)
            >>> enums["StatusEnum"].enum_var_names
            ["OPEN", "CLOSED"]
        """
        enums = {}

        def auto_generate_enum_var_names(schema: IRSchemaObject) -> IRSchemaObject:
            """Auto-generate enum_var_names from enum values if missing."""
            if schema.enum and not schema.enum_var_names:
                # Generate variable names from values
                var_names = []
                for value in schema.enum:
                    if isinstance(value, str):
                        # Convert "waiting_for_user" → "WAITING_FOR_USER"
                        var_name = value.upper().replace("-", "_").replace(" ", "_")
                    else:
                        # For integers: 1 → "VALUE_1"
                        var_name = f"VALUE_{value}"
                    var_names.append(var_name)

                # Create new schema with auto-generated var names
                schema = IRSchemaObject(
                    **{**schema.model_dump(), "enum_var_names": var_names}
                )
            return schema

        def collect_recursive(schema: IRSchemaObject):
            """Recursively collect enums from schema and its nested properties."""
            # Check if this schema itself is an enum (with or without x-enum-varnames)
            if schema.enum and schema.name:
                schema = auto_generate_enum_var_names(schema)
                enums[schema.name] = schema

            # Check if this schema is a reference to an enum
            if schema.ref and schema.ref in self.context.schemas:
                ref_schema = self.context.schemas[schema.ref]
                if ref_schema.enum:
                    ref_schema = auto_generate_enum_var_names(ref_schema)
                    enums[ref_schema.name] = ref_schema

            # Check properties for enums
            if schema.properties:
                for prop_schema in schema.properties.values():
                    # If property has enum, it's a standalone enum
                    if prop_schema.enum and prop_schema.name:
                        prop_schema = auto_generate_enum_var_names(prop_schema)
                        enums[prop_schema.name] = prop_schema
                    # Check if property is a reference to an enum
                    elif prop_schema.ref and prop_schema.ref in self.context.schemas:
                        ref_schema = self.context.schemas[prop_schema.ref]
                        if ref_schema.enum:
                            ref_schema = auto_generate_enum_var_names(ref_schema)
                            enums[ref_schema.name] = ref_schema
                    # Recurse into nested objects
                    elif prop_schema.type == "object":
                        collect_recursive(prop_schema)
                    # Recurse into arrays
                    elif prop_schema.type == "array" and prop_schema.items:
                        if prop_schema.items.enum and prop_schema.items.name:
                            items = auto_generate_enum_var_names(prop_schema.items)
                            enums[items.name] = items
                        elif prop_schema.items.ref and prop_schema.items.ref in self.context.schemas:
                            ref_items = self.context.schemas[prop_schema.items.ref]
                            if ref_items.enum:
                                ref_items = auto_generate_enum_var_names(ref_items)
                                enums[ref_items.name] = ref_items
                        elif prop_schema.items.type == "object":
                            collect_recursive(prop_schema.items)

            # Check array items for enums (if schema itself is array)
            if schema.items:
                if schema.items.enum and schema.items.name:
                    items = auto_generate_enum_var_names(schema.items)
                    enums[items.name] = items
                elif schema.items.ref and schema.items.ref in self.context.schemas:
                    ref_items = self.context.schemas[schema.items.ref]
                    if ref_items.enum:
                        ref_items = auto_generate_enum_var_names(ref_items)
                        enums[ref_items.name] = ref_items
                elif schema.items.type == "object":
                    collect_recursive(schema.items)

        # Collect enums from all schemas
        for schema in schemas.values():
            collect_recursive(schema)

        return enums

    def get_operations_by_tag(self) -> dict[str, list[IROperationObject]]:
        """Get operations grouped by tags."""
        return self.context.operations_by_tag

    def save_files(self, files: list[GeneratedFile], output_dir: Path) -> None:
        """
        Save generated files to disk.

        Args:
            files: List of GeneratedFile objects
            output_dir: Output directory path

        Examples:
            >>> files = generator.generate()
            >>> generator.save_files(files, Path("./generated"))
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            file_path = output_dir / file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file.content)

    # ===== Formatting Helpers =====

    def indent(self, code: str, spaces: int = 4) -> str:
        """
        Indent code by N spaces.

        Args:
            code: Code to indent
            spaces: Number of spaces (default: 4)

        Returns:
            Indented code

        Examples:
            >>> generator.indent("x = 1\\ny = 2", 4)
            '    x = 1\\n    y = 2'
        """
        lines = code.split("\n")
        indent_str = " " * spaces
        return "\n".join(f"{indent_str}{line}" if line.strip() else line for line in lines)

    def sanitize_name(self, name: str) -> str:
        """
        Sanitize schema/operation name to valid identifier.

        Args:
            name: Raw name

        Returns:
            Sanitized name

        Examples:
            >>> generator.sanitize_name("User-Profile")
            'User_Profile'
            >>> generator.sanitize_name("2Users")
            '_2Users'
        """
        # Replace invalid characters with underscore
        sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in name)

        # Ensure doesn't start with digit
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"

        return sanitized or "Unknown"

    def wrap_comment(self, text: str, max_length: int = 80) -> list[str]:
        """
        Wrap long comment text to multiple lines.

        Args:
            text: Comment text
            max_length: Maximum line length

        Returns:
            List of wrapped lines

        Examples:
            >>> generator.wrap_comment("This is a very long comment that should be wrapped", 30)
            ['This is a very long comment', 'that should be wrapped']
        """
        if not text:
            return []

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word) + (1 if current_line else 0)

            if current_length + word_length > max_length and current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += word_length

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def format_enum_description(self, text: str) -> str:
        """
        Format enum description by splitting bullet points.

        Enum descriptions from OpenAPI often have the format:
        "* `value1` - Desc1 * `value2` - Desc2"

        This method splits them into separate lines:
        "* `value1` - Desc1\n* `value2` - Desc2"

        Args:
            text: Enum description text

        Returns:
            Formatted description with proper line breaks
        """
        if not text:
            return text

        # Split by " * `" pattern (preserving the first *)
        import re
        # Replace " * `" with newline + "* `"
        formatted = re.sub(r'\s+\*\s+`', '\n* `', text.strip())

        return formatted

    def sanitize_enum_name(self, name: str) -> str:
        """
        Sanitize enum name by converting to PascalCase.

        Examples:
            "OrderDetail.status" -> "OrderDetailStatus"
            "Currency.currency_type" -> "CurrencyCurrencyType"
            "CurrencyList.currency_type" -> "CurrencyListCurrencyType"
            "User.role" -> "UserRole"

        Args:
            name: Original enum name (may contain dots, underscores)

        Returns:
            Sanitized PascalCase name
        """
        # Replace dots with underscores, then split and convert to PascalCase
        parts = name.replace('.', '_').split('_')
        result = []
        for word in parts:
            if not word:
                continue
            # If word is already PascalCase/camelCase, keep it as is
            # Otherwise capitalize first letter only
            if word[0].isupper():
                result.append(word)
            else:
                result.append(word[0].upper() + word[1:] if len(word) > 1 else word.upper())
        return ''.join(result)
