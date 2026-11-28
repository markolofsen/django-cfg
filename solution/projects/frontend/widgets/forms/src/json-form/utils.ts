import { isDev } from "@djangocfg/ui-core/lib";
import consola from 'consola';

import { RJSFSchema } from '@rjsf/utils';

/**
 * Utility functions for JSON Schema Form
 */

/**
 * Safely validates and normalizes JSON Schema
 * Ensures schema is valid before rendering
 */
export function validateSchema(schema: unknown): RJSFSchema | null {
  if (!schema || typeof schema !== 'object') {
    if (isDev) {
      consola.error('[JsonSchemaForm] Invalid schema: must be an object', schema);
    }
    return null;
  }

  // Basic schema validation - more permissive
  // Schema is valid if it has type OR properties OR $ref OR $schema
  const candidate = schema as Record<string, unknown>;
  const hasValidStructure =
    candidate.type ||
    candidate.properties ||
    candidate.$ref ||
    candidate.$schema;

  if (!hasValidStructure) {
    if (isDev) {
      consola.error('[JsonSchemaForm] Invalid schema: missing type, properties, $ref, or $schema', schema);
    }
    return null;
  }

  if (isDev) {
    consola.success('[JsonSchemaForm] Schema validated successfully:', {
      type: candidate.type,
      title: candidate.title,
      hasProperties: !!candidate.properties,
      hasRequired: !!candidate.required,
    });
  }

  return schema as RJSFSchema;
}

/**
 * Safely normalizes form data
 * Removes undefined values and ensures data structure matches schema
 */
export function normalizeFormData<T = unknown>(
  formData: unknown,
  schema: RJSFSchema
): T {
  if (formData === null || formData === undefined) {
    return (schema.type === 'object' ? {} : schema.type === 'array' ? [] : null) as T;
  }

  // Deep clone to avoid mutations
  const normalized = JSON.parse(JSON.stringify(formData));

  // Remove undefined values recursively
  return removeUndefined(normalized) as T;
}

/**
 * Recursively removes undefined values from an object
 */
function removeUndefined(obj: unknown): unknown {
  if (obj === null || obj === undefined) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(removeUndefined).filter((item) => item !== undefined);
  }

  if (typeof obj === 'object') {
    const source = obj as Record<string, unknown>;
    const cleaned: Record<string, unknown> = {};
    for (const key in source) {
      if (source[key] !== undefined) {
        cleaned[key] = removeUndefined(source[key]);
      }
    }
    return cleaned;
  }

  return obj;
}

/**
 * Merges schema defaults with form data
 */
export function mergeDefaults(
  formData: unknown,
  schema: RJSFSchema
): unknown {
  if (!schema) return formData;

  const result: Record<string, unknown> = { ...(formData as Record<string, unknown>) };

  if (schema.type === 'object' && schema.properties) {
    for (const [key, propSchema] of Object.entries(schema.properties)) {
      const prop = propSchema as RJSFSchema;

      // Apply default if field is missing
      if (result[key] === undefined && prop.default !== undefined) {
        result[key] = prop.default;
      }

      // Recursively merge nested objects
      if (prop.type === 'object' && result[key]) {
        result[key] = mergeDefaults(result[key], prop);
      }
    }
  }

  return result;
}

/**
 * Safely parses JSON string with error handling
 */
export function safeJsonParse<T = unknown>(
  jsonString: string,
  fallback: T
): T {
  try {
    return JSON.parse(jsonString);
  } catch (error) {
    consola.error('[JsonSchemaForm] JSON parse error:', error);
    return fallback;
  }
}

/**
 * Safely stringifies object to JSON
 */
export function safeJsonStringify(
  obj: unknown,
  pretty: boolean = true
): string {
  try {
    return JSON.stringify(obj, null, pretty ? 2 : 0);
  } catch (error) {
    consola.error('[JsonSchemaForm] JSON stringify error:', error);
    return '{}';
  }
}

/**
 * Checks if schema has required fields
 */
export function hasRequiredFields(schema: RJSFSchema): boolean {
  return Array.isArray(schema.required) && schema.required.length > 0;
}

/**
 * Gets all required field paths from schema
 */
export function getRequiredFields(
  schema: RJSFSchema,
  prefix: string = ''
): string[] {
  const required: string[] = [];

  if (schema.required && Array.isArray(schema.required)) {
    required.push(...schema.required.map((field) =>
      prefix ? `${prefix}.${field}` : field
    ));
  }

  if (schema.type === 'object' && schema.properties) {
    for (const [key, propSchema] of Object.entries(schema.properties)) {
      const prop = propSchema as RJSFSchema;
      const fieldPath = prefix ? `${prefix}.${key}` : key;
      required.push(...getRequiredFields(prop, fieldPath));
    }
  }

  return required;
}

/**
 * Validates form data against required fields
 */
export function validateRequiredFields(
  formData: unknown,
  schema: RJSFSchema
): { valid: boolean; missing: string[] } {
  const requiredFields = getRequiredFields(schema);
  const missing: string[] = [];

  for (const field of requiredFields) {
    const value = getNestedValue(formData, field);
    if (value === undefined || value === null || value === '') {
      missing.push(field);
    }
  }

  return {
    valid: missing.length === 0,
    missing,
  };
}

/**
 * Gets nested value from object by path
 */
function getNestedValue(obj: unknown, path: string): unknown {
  return path
    .split('.')
    .reduce<unknown>(
      (current, key) =>
        current && typeof current === 'object'
          ? (current as Record<string, unknown>)[key]
          : undefined,
      obj,
    );
}

import type { DisabledWhenRule } from './types';

/**
 * Evaluates a `ui:disabledWhen` rule against form data. Returns `true` when the
 * field should be disabled. If `rule` is undefined, returns `false`.
 *
 * Supported rule shapes:
 *   { path, eq } | { path, notEq } | { path, in } | { path, notIn }
 *   | { path, truthy: true } | { path, falsy: true }
 */
export function evaluateDisabledWhen(
  rule: DisabledWhenRule | undefined,
  formData: unknown,
): boolean {
  if (!rule) return false;
  const value = getNestedValue(formData, rule.path);
  if ('eq' in rule) return value === rule.eq;
  if ('notEq' in rule) return value !== rule.notEq;
  if ('in' in rule) return rule.in.includes(value);
  if ('notIn' in rule) return !rule.notIn.includes(value);
  if ('truthy' in rule) return Boolean(value);
  if ('falsy' in rule) return !value;
  return false;
}
