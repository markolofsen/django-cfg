# JsonForm

Schema-driven forms on top of [react-jsonschema-form](https://github.com/rjsf-team/react-jsonschema-form) (RJSF) with `@djangocfg/ui` widgets, AJV8 validation, and a few custom extensions for compact playground-style UIs.

```tsx
// Lazy entry — what production code should import. Ships only the
// component reference + a Suspense fallback; the ~300KB RJSF bundle
// loads on first mount.
import { LazyJsonSchemaForm } from '@djangocfg/ui-tools/json-form';

// Full entry — eager bundle. Use only for storybook / internal
// tooling that needs templates, widgets, or `evaluateDisabledWhen`
// at module scope. Pulls RJSF synchronously, no code-splitting.
import {
  JsonSchemaForm,
  ObjectFieldTemplate,
  evaluateDisabledWhen,
} from '@djangocfg/ui-tools/json-form/full';

const schema = {
  type: 'object',
  properties: {
    name: { type: 'string', title: 'Name' },
    age:  { type: 'integer', title: 'Age', minimum: 0 },
  },
};

<JsonSchemaForm schema={schema} onSubmit={(e) => console.log(e.formData)} />
```

---

## Components

| Export | Use |
|---|---|
| `JsonSchemaForm` | Direct (synchronous) form. |
| `LazyJsonSchemaForm` | Same API, lazy-loaded with a `<CardLoadingFallback>` (RJSF is ~300KB). |

Both accept the same `JsonSchemaFormProps`:

| Prop | Type | Notes |
|---|---|---|
| `schema` | `RJSFSchema` | Required. JSON Schema 7. |
| `uiSchema` | `UiSchema` | Optional. Widget overrides + custom extensions (see below). |
| `formData` | `T` | Initial / controlled data. |
| `onChange` | `(e) => void` | Live changes. |
| `onSubmit` | `(e) => void` | Submit (enter or button). |
| `onError` | `(errors) => void` | Validation errors. |
| `density` | `'comfortable' \| 'compact'` | Default `'comfortable'`. See **Density** below. |
| `liveValidate` | `boolean` | Default `false`. |
| `disabled` / `readonly` | `boolean` | Form-wide. |
| `showSubmitButton` | `boolean` | Default `true`. |
| `submitButtonText` | `string` | Default `'Submit'`. |
| `showErrorList` | `false \| 'top' \| 'bottom'` | Default `'top'`. |
| `className` | `string` | Wrapper class. |

---

## Built-in widgets

Mapped via `widgets={{ ... }}` and registered under both PascalCase and lowercase aliases — use whichever matches your `uiSchema`.

| `ui:widget` | Widget | Built on |
|---|---|---|
| `text` | `TextWidget` | `<Input />` |
| `number` | `NumberWidget` | `<Input type="number" />` |
| `checkbox` | `CheckboxWidget` | `<Checkbox />` |
| `switch` | `SwitchWidget` | `<Switch />` |
| `select` | `SelectWidget` | `<Select />` (auto-falls back to `<input type="text">` when no enum) |
| `slider` / `range` | `SliderWidget` | `<Slider />` (+ optional inline numeric input, supports unit suffix) |
| `color` | `ColorWidget` | Native colour picker. |

### Slider options

```ts
'ui:widget': 'slider',
'ui:options': {
  unit: 'px',        // appended to the displayed value: "12px"
  step: 2,
  showInput: false,  // hide the editable text input next to the slider
}
```

---

## Templates

Custom RJSF templates live in `./templates/`:

- `FieldTemplate` — label + body + errors. Honors `density`.
- `ObjectFieldTemplate` — object body. Supports `ui:collapsible`, `ui:grid`, `ui:className`, and **`ui:groups`** (see below).
- `ArrayFieldTemplate`, `ArrayFieldItemTemplate` — array editing.
- `ErrorListTemplate` — top/bottom error block.
- `BaseInputTemplate` — fallback input wrapper.

---

## Custom extensions

These are extra `uiSchema` keys this fork understands on top of stock RJSF.

### `density`

Form-wide compact mode. Drives label sizing, row spacing, and tooltip placement.

```tsx
<JsonSchemaForm density="compact" ... />
```

In compact mode:
- Labels: 10px uppercase muted, no description paragraph
- Description (`schema.description` or `ui:description`) becomes a `title=` tooltip on the label
- Tighter row spacing (`space-y-1` vs `space-y-2`)
- Slimmer select trigger (`h-7`) and inputs

Use this for sidebars, settings drawers, dense playground configurators.

### `ui:disabledWhen`

Declarative conditional disable, evaluated against the current `formData`. Avoids the JSON Schema `dependencies` boilerplate when you just want to grey a field out.

```ts
const uiSchema = {
  shell: {
    inset: {
      'ui:widget': 'slider',
      'ui:disabledWhen': { path: 'shell.variant', notEq: 'boxed' },
    },
  },
};
```

Supported rule shapes:

| Shape | Disabled when |
|---|---|
| `{ path, eq: value }` | field at `path` equals `value` |
| `{ path, notEq: value }` | field at `path` does not equal `value` |
| `{ path, in: [...] }` | field is in array |
| `{ path, notIn: [...] }` | field is not in array |
| `{ path, truthy: true }` | field is truthy |
| `{ path, falsy: true }` | field is falsy / empty / `false` / `0` |

`path` is dot-separated against `formData` root (e.g. `'shell.variant'`, `'navbar.controls.showThemeSwitcher'`).

The runtime `evaluateDisabledWhen(rule, formData)` is exported for tests / reuse.

### `ui:groups` (in `ObjectFieldTemplate`)

Splits a flat object into collapsible sub-sections without restructuring the schema.

```ts
sidebar: {
  'ui:groups': [
    { title: 'Density', fields: ['density'], defaultOpen: true },
    { title: 'Slots',   fields: ['showMenuStart', 'showMenuEnd'], defaultOpen: false },
    { title: 'Visual',  fields: ['activeIndicator', 'groupLabelStyle'] },
  ],
}
```

Fields not listed in any group render flat above the groups. Each group is a `<Collapsible>` with a chevron-right header.

### `ui:collapsible` / `ui:collapsed` (existing)

Wraps the entire object in a single collapsible card. Independent of `ui:groups` — use one or the other on a given object.

### `ui:grid` (existing)

`'ui:grid': 2` switches the object body to a 2-column grid (`gap-4`). Default is vertical stack.

---

## Example — playground sidebar

The `apps/demo` layouts playground uses the stack end-to-end:

```ts
// schema
const privateSchema: RJSFSchema = {
  type: 'object',
  properties: {
    shell: { type: 'object', properties: { variant: { type: 'string', enum: ['full-bleed', 'boxed'] }, inset: { type: 'integer', minimum: 0, maximum: 32 } } },
    sidebar: { type: 'object', properties: { /* ... */ } },
  },
};

// uiSchema
const privateUiSchema: UiSchema = {
  shell: {
    'ui:collapsible': true,
    inset: {
      'ui:widget': 'slider',
      'ui:options': { unit: 'px', step: 2, showInput: false },
      'ui:disabledWhen': { path: 'shell.variant', notEq: 'boxed' },
    },
  },
  sidebar: {
    'ui:collapsible': true,
    'ui:groups': [
      { title: 'Density', fields: ['density'], defaultOpen: true },
      { title: 'Visual',  fields: ['activeIndicator', 'groupLabelStyle'] },
    ],
  },
};

// component
<LazyJsonSchemaForm
  schema={privateSchema}
  uiSchema={privateUiSchema}
  formData={config}
  onChange={(e) => setConfig(e.formData)}
  density="compact"
  showSubmitButton={false}
  liveValidate={false}
/>
```

See `apps/demo/.../layouts/sidebar/{private,public}/Sidebar.tsx` for the full integration.

---

## Internals

| File | Role |
|---|---|
| `JsonSchemaForm.tsx` | Top-level component. Validates schema, normalises `formData`, threads `formContext = { density, formData }` to widgets/templates. |
| `widgets/_useWidgetEnv.ts` | Internal hook reading density + `ui:disabledWhen` from `formContext`. Used by `Switch`, `Select`, `Slider`, `Checkbox`. |
| `templates/ObjectFieldTemplate.tsx` | Implements `ui:collapsible`, `ui:grid`, `ui:groups`. |
| `templates/FieldTemplate.tsx` | Density-aware label / description / errors layout. |
| `utils.ts` | `validateSchema`, `normalizeFormData`, `evaluateDisabledWhen`, plus default-merging helpers. |

---

## Re-exported types

For consumers that don't have `@rjsf/utils` as a direct dependency:

```ts
import type {
  RJSFSchema,
  UiSchema,
  JsonSchemaFormProps,
  JsonFormDensity,
  DisabledWhenRule,
  UiGroup,
  JsonFormContext,
} from '@djangocfg/ui-tools/json-form';
```

### Portable schema types (`CustomJson*`)

For packages that **ship a configurator schema** without taking a runtime
dependency on RJSF — typically library packages like `@djangocfg/layouts/configurator`
— use the portable types from `@djangocfg/ui-core/lib`:

```ts
import type {
  CustomJsonSchema7,
  CustomJsonSchema7Type,
  CustomJsonUiSchema7,
  CustomJsonUiGroup,
  CustomJsonUiDisabledWhenRule,
} from '@djangocfg/ui-core/lib';

// also re-exported from `@djangocfg/ui-tools` for convenience.
```

These are our own Draft 7-shaped subset (not a copy of RJSF's types) and
`<JsonSchemaForm>` accepts them directly via union with `RJSFSchema`. Library
packages typing their schemas with `CustomJsonSchema7` stay decoupled from
the form framework — if RJSF is ever swapped out, these schemas don't need
to change.

The aliases `DisabledWhenRule` and `UiGroup` exported from `@djangocfg/ui-tools`
point at `CustomJsonUiDisabledWhenRule` / `CustomJsonUiGroup` respectively
(kept for back-compat with existing consumers).
