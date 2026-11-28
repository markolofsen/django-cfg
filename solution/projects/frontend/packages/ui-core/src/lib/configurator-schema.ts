/**
 * Shared types for schema-driven configurator UIs in the djangocfg monorepo.
 *
 * This is **our** mini-spec — a Draft 7-shaped subset that any package can use
 * to describe a configurator without taking a runtime dependency on RJSF or
 * any other form framework. `@djangocfg/ui-tools`'s `<JsonSchemaForm>` accepts
 * these types directly (it casts internally to RJSF's own types).
 *
 * Use this when you ship a configurator schema from a non-form package
 * (e.g. `@djangocfg/layouts/configurator`) so the package stays decoupled
 * from any concrete form framework.
 *
 * Naming choice: not `JsonSchema` (would clash with the broader Draft 7 spec
 * and other community types). `CustomJsonSchema7` makes the scope explicit:
 * this is for sidebar / settings configurators, not arbitrary JSON validation.
 */

/** Primitive JSON Schema types we cover. */
export type CustomJsonSchema7Type =
  | 'object'
  | 'array'
  | 'string'
  | 'number'
  | 'integer'
  | 'boolean'
  | 'null';

/** A Draft 7-shaped JSON Schema descriptor — sufficient for configurator UIs. */
export interface CustomJsonSchema7 {
  type?: CustomJsonSchema7Type;
  title?: string;
  description?: string;
  default?: unknown;
  enum?: readonly (string | number | boolean | null)[];
  /** Whitelist of property keys that must be set (objects only). */
  required?: readonly string[];
  /** Object child schemas. */
  properties?: Record<string, CustomJsonSchema7>;
  /** Array item schema. */
  items?: CustomJsonSchema7;
  /** Numeric bounds. */
  minimum?: number;
  maximum?: number;
  /** String / array bounds. */
  minLength?: number;
  maxLength?: number;
  /** String format (e.g. `'email'`, `'uri'`). */
  format?: string;
  /** Free-form extras kept as-is — let downstream form frameworks read them. */
  [key: string]: unknown;
}

/**
 * Conditional-disable rule attached to a field via `'ui:disabledWhen'` in
 * `CustomJsonUiSchema7`. Evaluated against the form's current data by the
 * runtime (`@djangocfg/ui-tools`'s `evaluateDisabledWhen`).
 */
export type CustomJsonUiDisabledWhenRule =
  | { path: string; eq: unknown }
  | { path: string; notEq: unknown }
  | { path: string; in: readonly unknown[] }
  | { path: string; notIn: readonly unknown[] }
  | { path: string; truthy: true }
  | { path: string; falsy: true };

/**
 * Sub-group descriptor used by `'ui:groups'` on an object's uiSchema. Splits
 * the object into collapsible sub-sections without restructuring the schema.
 */
export interface CustomJsonUiGroup {
  /** Section title shown on the trigger row. */
  title: string;
  /** Property keys to include in this group. */
  fields: readonly string[];
  /** Initial open state. Default `true`. */
  defaultOpen?: boolean;
}

/**
 * Per-field UI hints that travel alongside `CustomJsonSchema7`. Mirrors the
 * subset of RJSF `uiSchema` we use, plus our own `ui:disabledWhen`
 * / `ui:groups` extensions.
 */
export interface CustomJsonUiSchema7 {
  /** Override the widget for this field (`'select'`, `'switch'`, `'slider'`, `'textarea'`, …). */
  'ui:widget'?: string;
  /** Free-form widget options (e.g. `{ unit: 'px', step: 2 }` for slider). */
  'ui:options'?: Record<string, unknown>;
  /** Description override; in compact density the value moves into the label tooltip. */
  'ui:description'?: string;
  /** Wrap this object body in a single Collapsible card. */
  'ui:collapsible'?: boolean;
  /** Initial collapsed state when `ui:collapsible`. Default `false` (open). */
  'ui:collapsed'?: boolean;
  /** Grid column count for an object body (1, 2, 3 …). */
  'ui:grid'?: number;
  /** Extra wrapper class. */
  'ui:className'?: string;
  /** Split an object into collapsible sub-sections. */
  'ui:groups'?: readonly CustomJsonUiGroup[];
  /** Declarative conditional disable. */
  'ui:disabledWhen'?: CustomJsonUiDisabledWhenRule;
  /** Per-property nested uiSchema (keys mirror `properties` keys on the schema). */
  [key: string]: unknown;
}
