# Django Admin widgets

Form widgets for the `django_admin` module, and the registry that renders the
`ui_widget` display names. Two different things live here; do not mix them.

| | Controls | Declared in | Code |
|---|---|---|---|
| Display widgets | how a value is shown in the changelist and in readonly fields | `display_fields=[BadgeField(...), ...]` (the `ui_widget` of each field class) | `WidgetRegistry` in `registry.py` |
| Form widgets | the input in the edit form | `AdminConfig(widgets=[JSONWidgetConfig(...)])` | `JSONEditorWidget` and the config models in `config/widget_config.py` |

## JSONEditorWidget (wired)

`JSONEditorWidget` extends django-json-widget with a copy button and Unfold light or
dark theme switching (template `django_admin/widgets/json_editor.html`, CSS
`django_admin/css/json_editor_theme.css`). `PydanticAdmin.formfield_for_dbfield`
applies it **to every editable `JSONField`**, so no configuration is needed. A field
listed in `readonly_fields` keeps the plain display. The defaults of the auto-applied
widget are `mode="code"` (modes code, tree, view) and `height="400px"`; the widget
class itself defaults to `mode="tree"` when you build it by hand.

Tune one field with `JSONWidgetConfig`:

```python
from django_cfg.modules.django_admin import AdminConfig, JSONWidgetConfig

config = AdminConfig(
    model=Bot,
    widgets=[
        JSONWidgetConfig(field="settings", mode="tree", height="500px", show_copy_button=True),
    ],
)
```

Fields: `mode` (`"tree"`, `"code"`, `"view"`; default `"code"`), `height` (`"400px"`),
`width` (none), `show_copy_button` (`True`).

## What `AdminConfig.widgets` really does

`PydanticAdmin` reads each entry's `field` and `to_widget_kwargs()` into a per-field
table, and `formfield_for_dbfield` consults that table **only for `JSONField`s**. So:

- `JSONWidgetConfig` works as above;
- `TextWidgetConfig` (`placeholder`, `max_length`, `rows`) and `ImagePreviewWidgetConfig`
  (thumbnail size, zoom and pan options) validate and are accepted, but nothing
  applies them to a text or file field today;
- `ImagePreviewWidget` (a `ClearableFileInput` with a zoom and pan modal, template
  `django_admin/widgets/image_preview.html`) exists but is not applied automatically.
  Use it yourself in a form: `widget=ImagePreviewWidget(...)`, importing it from
  `django_cfg.modules.django_admin.widgets.image_preview_widget`. For the changelist
  use the `ImagePreviewField` display field instead.

A new config class for another field type therefore needs a hook in
`formfield_for_dbfield` as well; a class on its own changes nothing.

## Geo widgets

`CountrySelectWidget`, `CitySelectWidget` and `LocationSelectWidget` (Select2-style
autocomplete selects fed from the geo app, `django_cfg.apps.tools.geo`) are exported
lazily from `django_cfg.modules.django_admin.widgets`. They depend on libraries that
read Django settings at import, hence the PEP 562 `__getattr__` in `__init__.py`:
import them inside functions or after setup, not at the top of `config.py`.
A model field of class `LocationField` gets `LocationFieldWidget` (map preview) from
the same hook.

Money fields use `MoneyFieldWidget` from `django_cfg.modules.django_currency.widgets`,
through `MoneyFieldAdminMixin`, not from this folder.

## WidgetRegistry: display handlers

`WidgetRegistry` maps a `ui_widget` name to a render function
`(obj, field_name, config) -> SafeString`. It is **not** a registry of form widget
classes. Built-in names include `badge`, `progress`, `counter`, `datetime_relative`,
`datetime_compact`, `text`, `boolean`, `decimal`, `image`, `image_preview`,
`json_editor`, `link`, `status_badges`, `short_uuid`, `stacked`, `markdown`,
`user_avatar`, `user_simple`, `currency`, `money_breakdown`, `money_field`, `country`,
`city`, `location`.

```python
from django_cfg.modules.django_admin import WidgetRegistry

def render_phone(obj, field_name, config):
    from django.utils.html import format_html
    return format_html("<code>{}</code>", getattr(obj, field_name))

WidgetRegistry.register("phone", render_phone)   # a handler, not a widget class
handler = WidgetRegistry.get("phone")
```

An unknown name logs a warning and falls back to the raw value; a handler that raises
is logged and falls back the same way. A custom name only helps where something emits
it as `ui_widget`, so most projects use the built-in field classes instead.

Authoritative lists: `@docs/field-types.md` (display fields) and `@docs/api-reference.md`.
