"""
Resource configuration for import/export functionality.
"""

from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ResourceConfig(BaseModel):
    """
    Configuration for django-import-export Resource class.

    Provides declarative configuration for import/export behavior without
    needing to manually create Resource classes.

    Example:
        ```python
        resource_config = ResourceConfig(
            fields=['host', 'port', 'username', 'password', 'provider'],
            exclude=['metadata', 'config'],
            import_id_fields=['host', 'port'],
            after_import_row='apps.proxies.services.test_proxy_async',
            skip_unchanged=True,
        )
        ```
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True
    )

    # Field configuration
    fields: List[str] = Field(
        default_factory=list,
        description="Fields to include in import/export (empty = all fields)"
    )
    exclude: List[str] = Field(
        default_factory=list,
        description="Fields to exclude from import/export"
    )
    import_id_fields: List[str] = Field(
        default_factory=lambda: ['id'],
        description="Fields used to identify existing rows during import"
    )

    # Import behavior
    skip_unchanged: bool = Field(
        True,
        description="Skip rows that haven't changed during import"
    )
    report_skipped: bool = Field(
        True,
        description="Include skipped rows in import report"
    )
    skip_diff: bool = Field(
        False,
        description="Skip diff generation for faster imports (large datasets)"
    )
    use_transactions: bool = Field(
        True,
        description="Use database transactions for imports"
    )

    # Validation and hooks (can be string paths or callables)
    before_import: Optional[Union[str, Callable]] = Field(
        None,
        description="Hook called before import starts (receives dataset, dry_run)"
    )
    after_import: Optional[Union[str, Callable]] = Field(
        None,
        description="Hook called after import completes (receives dataset, result, dry_run)"
    )
    before_import_row: Optional[Union[str, Callable]] = Field(
        None,
        description="Hook called before each row import (receives row, row_number, dry_run)"
    )
    after_import_row: Optional[Union[str, Callable]] = Field(
        None,
        description="Hook called after each row import (receives row, row_result, row_number)"
    )

    # Export options
    export_order: List[str] = Field(
        default_factory=list,
        description="Field order in exported files (empty = model field order)"
    )

    # Field widgets/customization
    field_widgets: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom widgets for fields (e.g., {'date': {'format': '%Y-%m-%d'}})"
    )

    # Batch processing
    batch_size: Optional[int] = Field(
        None,
        description="Process imports in batches (for large datasets)"
    )

    def get_callable(self, hook_name: str) -> Optional[Callable]:
        """
        Get callable for a hook by name.

        Args:
            hook_name: Name of the hook ('before_import', 'after_import_row', etc.)

        Returns:
            Callable function or None if not set
        """
        hook_value = getattr(self, hook_name, None)

        if hook_value is None:
            return None

        # If already a callable, return it
        if callable(hook_value):
            return hook_value

        # If string, import it
        if isinstance(hook_value, str):
            import importlib
            module_path, function_name = hook_value.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, function_name)

        return None
