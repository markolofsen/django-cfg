"use client"

/**
 * JSON Schema Form Module
 *
 * A complete solution for generating forms from JSON Schema 7
 * Built with React JSON Schema Form (rjsf), Radix UI, and Tailwind CSS
 *
 * Features:
 * - Automatic form generation from JSON Schema
 * - Custom widgets using @djangocfg/ui components
 * - Validation with ajv8
 * - TypeScript support
 * - Responsive design
 * - Dark mode support
 *
 * @example
 * ```tsx
 * import { JsonSchemaForm } from '@/common/JsonForm';
 *
 * const schema = {
 *   type: 'object',
 *   properties: {
 *     name: { type: 'string' },
 *     age: { type: 'number' }
 *   }
 * };
 *
 * <JsonSchemaForm
 *   schema={schema}
 *   onSubmit={(data) => console.log(data)}
 * />
 * ```
 */

export { JsonSchemaForm } from './JsonSchemaForm';
export type {
  JsonSchemaFormProps,
  JsonFormDensity,
  DisabledWhenRule,
  UiGroup,
  JsonFormContext,
} from './types';
export { evaluateDisabledWhen } from './utils';

// Re-export RJSF schema types so consumers don't need to install `@rjsf/utils`
// directly. Keeps this widget the single dependency for schema-driven forms.
export type { RJSFSchema, UiSchema } from '@rjsf/utils';

// Re-export the portable schema types from ui-core for convenience: most
// configurator authors only need these (no RJSF coupling).
export type {
  CustomJsonSchema7,
  CustomJsonSchema7Type,
  CustomJsonUiSchema7,
  CustomJsonUiGroup,
  CustomJsonUiDisabledWhenRule,
} from '@djangocfg/ui-core/lib';

// Export widgets for custom usage
export * from './widgets';

// Export templates for custom usage
export * from './templates';

// Export utilities for advanced usage
export * from './utils';
