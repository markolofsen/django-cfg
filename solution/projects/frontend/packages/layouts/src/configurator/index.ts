/**
 * JSON Schema descriptors for `<JsonSchemaForm>`-driven layout configurators.
 *
 * Drop a schema + uiSchema into `@djangocfg/widget-forms`'s `<JsonSchemaForm>` and
 * you get a ready-made sidebar that edits the matching `<Layout>` props live.
 *
 * Public surface today:
 *   - `private` — `PrivateLayout` configurator (shell + sidebar + header)
 *   - `auth`    — `AuthLayout` configurator (centered / split variants)
 *
 * Public + theme configurators are not exported yet — they currently live in
 * the demo app while the schema shape is iterated on.
 */

export * from './private';
export * from './auth';
