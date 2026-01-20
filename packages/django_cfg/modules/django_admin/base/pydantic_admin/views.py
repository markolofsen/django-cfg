"""
View overrides for admin.

Provides changelist_view, changeform_view, get_fieldsets, and formfield_for_dbfield.
"""

import logging
from pathlib import Path
from typing import Optional

from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


class ViewMixin:
    """
    Mixin providing view-related overrides for ModelAdmin.

    Includes:
    - changelist_view with documentation context
    - changeform_view with documentation context
    - get_fieldsets for filtering non-editable fields on add form
    - formfield_for_dbfield for JSON and encrypted field widgets
    """

    def _get_app_path(self) -> Optional[Path]:
        """
        Detect the app path for relative file resolution.

        Returns:
            Path to the app directory or None
        """
        if not self.model:
            return None

        try:
            # Get app label from model
            app_label = self.model._meta.app_label

            # Try to get app config
            from django.apps import apps
            app_config = apps.get_app_config(app_label)

            if app_config and hasattr(app_config, 'path'):
                return Path(app_config.path)
        except Exception as e:
            logger.warning(f"Could not detect app path for {self.model}: {e}")

        return None

    def get_queryset(self, request):
        """Apply select_related, prefetch_related, and annotations from config."""
        qs = super().get_queryset(request)

        # Auto-apply optimizations from config
        if self.config.select_related:
            qs = qs.select_related(*self.config.select_related)

        if self.config.prefetch_related:
            qs = qs.prefetch_related(*self.config.prefetch_related)

        # Auto-apply annotations from config
        if self.config.annotations:
            qs = qs.annotate(**self.config.annotations)

        return qs

    def get_fieldsets(self, request, obj=None):
        """
        Return fieldsets, filtering out non-editable fields from add form.

        For add form (obj=None), we exclude fields that are:
        - auto_now_add=True (created_at, etc)
        - auto_now=True (updated_at, etc)
        - auto-generated (id, uuid, etc)
        - methods (not actual model fields)

        For change form (obj exists), we show all fieldsets as-is.
        """
        fieldsets = super().get_fieldsets(request, obj)

        # For change form, return fieldsets as-is (readonly fields will be shown)
        if obj is not None:
            return fieldsets

        # For add form, filter out non-editable fields
        if not fieldsets:
            return fieldsets

        # Get all actual model field names
        model_field_names = set()
        for field in self.model._meta.get_fields():
            model_field_names.add(field.name)

        # Get non-editable field names
        non_editable_fields = set()
        for field in self.model._meta.get_fields():
            if hasattr(field, 'editable') and not field.editable:
                non_editable_fields.add(field.name)
            # Also check for auto_now and auto_now_add
            if hasattr(field, 'auto_now') and field.auto_now:
                non_editable_fields.add(field.name)
            if hasattr(field, 'auto_now_add') and field.auto_now_add:
                non_editable_fields.add(field.name)

        # Filter fieldsets
        filtered_fieldsets = []
        for name, options in fieldsets:
            if 'fields' in options:
                # Filter out non-editable fields and non-model fields from this fieldset
                filtered_fields = [
                    f for f in options['fields']
                    if f in model_field_names and f not in non_editable_fields
                ]

                # Only include fieldset if it has remaining fields
                if filtered_fields:
                    filtered_options = options.copy()
                    filtered_options['fields'] = tuple(filtered_fields)
                    filtered_fieldsets.append((name, filtered_options))
            else:
                # Keep fieldsets without 'fields' key as-is
                filtered_fieldsets.append((name, options))

        return tuple(filtered_fieldsets)

    def changelist_view(self, request, extra_context=None):
        """Override to add documentation context to changelist."""
        if extra_context is None:
            extra_context = {}

        # Add documentation context if configured
        if hasattr(self, 'documentation_config') and self.documentation_config:
            doc_config = self.documentation_config
            app_path = self._get_app_path()

            if doc_config.show_on_changelist:
                extra_context['documentation_config'] = doc_config
                extra_context['documentation_sections'] = doc_config.get_sections(app_path)

                # Add tree structure for modal view
                import json
                tree_structure = doc_config.get_tree_structure(app_path)
                extra_context['documentation_tree'] = mark_safe(json.dumps(tree_structure))
                extra_context['documentation_sections_count'] = len(doc_config.get_sections(app_path))

                # Add management commands if enabled
                if doc_config.show_management_commands:
                    extra_context['management_commands'] = doc_config._discover_management_commands(app_path)

                # Add Mermaid resources if plugins enabled
                if doc_config.enable_plugins:
                    from django_cfg.modules.django_admin.utils.markdown.mermaid_plugin import get_mermaid_resources
                    extra_context['mermaid_resources'] = get_mermaid_resources()

        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Override to add documentation context to changeform."""
        if extra_context is None:
            extra_context = {}

        # Store object in request for formfield_for_dbfield (MoneyFieldAdminMixin)
        if object_id:
            try:
                request._editing_obj = self.get_object(request, object_id)
            except Exception:
                pass

        # Add documentation context if configured
        if hasattr(self, 'documentation_config') and self.documentation_config:
            doc_config = self.documentation_config
            app_path = self._get_app_path()

            if doc_config.show_on_changeform:
                extra_context['documentation_config'] = doc_config
                extra_context['documentation_sections'] = doc_config.get_sections(app_path)

                # Add tree structure for modal view
                import json
                tree_structure = doc_config.get_tree_structure(app_path)
                extra_context['documentation_tree'] = mark_safe(json.dumps(tree_structure))
                extra_context['documentation_sections_count'] = len(doc_config.get_sections(app_path))

                # Add management commands if enabled
                if doc_config.show_management_commands:
                    extra_context['management_commands'] = doc_config._discover_management_commands(app_path)

                # Add Mermaid resources if plugins enabled
                if doc_config.enable_plugins:
                    from django_cfg.modules.django_admin.utils.markdown.mermaid_plugin import get_mermaid_resources
                    extra_context['mermaid_resources'] = get_mermaid_resources()

        return super().changeform_view(request, object_id, form_url, extra_context)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Override form field for specific database field types.

        Automatically detects and customizes:
        - JSON fields (applies django-json-widget for editable fields only)
        - Encrypted fields from django-crypto-fields

        Note: MoneyField is handled by MoneyFieldAdminMixin from django_currency module.
        """
        field_class_name = db_field.__class__.__name__

        # Auto-apply JSONEditorWidget for editable JSON fields (not readonly)
        if field_class_name == 'JSONField':
            # Check if field is editable (not in readonly_fields)
            is_readonly = db_field.name in self.readonly_fields

            # Only apply for editable fields
            if not is_readonly:
                try:
                    # Use our custom JSONEditorWidget with Unfold theme support
                    from ...widgets import JSONEditorWidget

                    # Get field-specific config from AdminConfig.widgets
                    field_widget_config = getattr(self.__class__, '_field_widget_configs', {}).get(db_field.name, {})

                    # Default widget settings with Unfold theme support
                    widget_kwargs = {
                        'mode': 'code',
                        'height': '400px',
                        'options': {
                            'modes': ['code', 'tree', 'view'],
                            # Unfold dark theme colors
                            'mainMenuBar': True,
                            'navigationBar': False,
                        }
                    }

                    # Override with field-specific config
                    if field_widget_config:
                        widget_kwargs.update(field_widget_config)
                        logger.debug(f"Applied custom JSONWidget config for '{db_field.name}': {field_widget_config}")

                    # Apply JSONEditorWidget (overrides Unfold's UnfoldAdminTextareaWidget)
                    kwargs['widget'] = JSONEditorWidget(**widget_kwargs)
                    logger.debug(f"Auto-applied JSONEditorWidget to editable field '{db_field.name}'")
                except ImportError:
                    logger.warning("django-json-widget not available, using default textarea")

        # Check if this is an EncryptedTextField or EncryptedCharField
        if 'Encrypted' in field_class_name and ('TextField' in field_class_name or 'CharField' in field_class_name):
            from django import forms
            from ...widgets import EncryptedFieldWidget, EncryptedPasswordWidget

            # Determine placeholder based on field name
            placeholder = "Enter value"
            if 'key' in db_field.name.lower():
                placeholder = "Enter API Key"
            elif 'secret' in db_field.name.lower():
                placeholder = "Enter API Secret"
            elif 'passphrase' in db_field.name.lower():
                placeholder = "Enter Passphrase (if required)"

            # Widget attributes
            widget_attrs = {
                'placeholder': placeholder,
            }

            # Decide widget based on config
            show_plain_text = getattr(self.config, 'show_encrypted_fields_as_plain_text', False)

            if show_plain_text:
                # Show as plain text with copy button
                widget = EncryptedFieldWidget(attrs=widget_attrs, show_copy_button=True)
            else:
                # Show as password (masked) with copy button
                # render_value=True shows masked value (••••••) after save
                widget = EncryptedPasswordWidget(attrs=widget_attrs, render_value=True, show_copy_button=True)

            # Return CharField with appropriate widget
            return forms.CharField(
                widget=widget,
                required=not db_field.blank and not db_field.null,
                help_text=db_field.help_text or "This field is encrypted at rest",
                label=db_field.verbose_name if hasattr(db_field, 'verbose_name') else db_field.name.replace('_', ' ').title()
            )

        # Handle LocationField with custom widget
        if field_class_name == 'LocationField':
            try:
                from django_cfg.apps.tools.geo.widgets.location_widget import LocationFieldWidget

                # Get initial values from existing object if editing
                widget_attrs = {}
                obj = getattr(request, '_editing_obj', None)
                if obj:
                    widget_attrs['initial_address'] = getattr(obj, 'address', '') or ''
                    widget_attrs['initial_latitude'] = getattr(obj, 'latitude', '') or ''
                    widget_attrs['initial_longitude'] = getattr(obj, 'longitude', '') or ''

                kwargs['widget'] = LocationFieldWidget(
                    attrs=widget_attrs,
                    show_map=True,
                    map_height="160px",
                )
                logger.debug(f"Auto-applied LocationFieldWidget to field '{db_field.name}'")
            except ImportError:
                logger.warning("LocationFieldWidget not available, using default widget")

        # Fall back to default Django behavior
        return super().formfield_for_dbfield(db_field, request, **kwargs)
