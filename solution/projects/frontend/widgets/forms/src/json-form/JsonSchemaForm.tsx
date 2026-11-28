'use client';

import consola from 'consola';
import { isDev } from '@djangocfg/ui-core/lib';
import { AlertCircle } from 'lucide-react';
import React, { useCallback, useMemo } from 'react';

import { Alert, AlertDescription, Button } from '@djangocfg/ui-core/components';
import Form, { type IChangeEvent } from '@rjsf/core';
import { RegistryWidgetsType, RJSFValidationError, UiSchema } from '@rjsf/utils';
import validator from '@rjsf/validator-ajv8';

import {
    ArrayFieldItemTemplate, ArrayFieldTemplate, BaseInputTemplate, ErrorListTemplate, FieldTemplate,
    ObjectFieldTemplate
} from './templates';
import { JsonFormContext, JsonSchemaFormProps } from './types';
import { normalizeFormData, validateSchema } from './utils';
import {
    CheckboxWidget, ColorWidget, NumberWidget, RadioWidget, SelectWidget, SliderWidget, SwitchWidget,
    TextareaWidget, TextWidget
} from './widgets';

/**
 * JSON Schema Form Component
 *
 * A fully-featured form generator that creates forms from JSON Schema.
 * Built on top of react-jsonschema-form with custom widgets and templates
 * using @djangocfg/ui components.
 *
 * @example
 * ```tsx
 * const schema = {
 *   type: 'object',
 *   required: ['name'],
 *   properties: {
 *     name: { type: 'string', title: 'Name' },
 *     age: { type: 'number', title: 'Age' },
 *     active: { type: 'boolean', title: 'Active' }
 *   }
 * };
 *
 * <JsonSchemaForm
 *   schema={schema}
 *   onSubmit={(data) => console.log(data.formData)}
 * />
 * ```
 */
export function JsonSchemaForm<T = unknown>(props: JsonSchemaFormProps<T>) {
  const {
    schema,
    uiSchema,
    formData,
    onSubmit,
    onChange,
    onError,
    showErrorList = 'top',
    liveValidate = false,
    disabled = false,
    readonly = false,
    className,
    showSubmitButton = true,
    submitButtonText = 'Submit',
    density = 'comfortable',
    formContext: callerFormContext,
    ...restProps
  } = props;

  // Validate and normalize schema before render
  const validatedSchema = useMemo(() => {
    if (isDev) {
      consola.info('[JsonSchemaForm] Validating schema...', schema);
    }
    const result = validateSchema(schema);
    if (!result && isDev) {
      consola.error('[JsonSchemaForm] Schema validation failed');
    }
    return result;
  }, [schema]);

  // Normalize form data before render
  const normalizedFormData = useMemo(() => {
    if (!validatedSchema) {
      if (isDev) {
        consola.warn('[JsonSchemaForm] Cannot normalize formData - invalid schema');
      }
      // `undefined`, not `null`: RJSF's `formData` accepts only `T | undefined`,
      // and the invalid-schema branch below early-returns before rendering it.
      return undefined;
    }
    if (isDev) {
      consola.info('[JsonSchemaForm] Normalizing formData...', formData);
    }
    const normalized = normalizeFormData<T>(formData, validatedSchema);
    if (isDev) {
      consola.info('[JsonSchemaForm] Normalized formData:', normalized);
    }
    return normalized;
  }, [formData, validatedSchema]);

  // Memoize widgets mapping to prevent recreation on every render
  // IMPORTANT: Widget keys must match RJSF's expected names:
  // - For type: string -> uses 'TextWidget' or 'text'
  // - For type: number/integer -> uses 'updown' or 'range'
  // - For type: boolean -> uses 'checkbox' or 'select'
  // - For enum fields -> uses 'SelectWidget' or 'select'
  const widgets: RegistryWidgetsType = useMemo(() => ({
    // Standard widget names (PascalCase) - used by RJSF internally
    TextWidget,
    TextareaWidget,
    NumberWidget,
    CheckboxWidget,
    SelectWidget,
    RadioWidget,
    SwitchWidget,
    ColorWidget,
    SliderWidget,
    // Lowercase aliases - for uiSchema 'ui:widget' references
    text: TextWidget,
    textarea: TextareaWidget,
    number: NumberWidget,
    checkbox: CheckboxWidget,
    select: SelectWidget,
    radio: RadioWidget,
    switch: SwitchWidget,
    color: ColorWidget,
    slider: SliderWidget,
    range: SliderWidget, // alias
  }), []);

  // Validate uiSchema widget references and strip unknown ones so RJSF
  // doesn't crash with "No widget 'xxx' for type 'yyy'".
  const safeUiSchema = useMemo(() => {
    if (!uiSchema) return uiSchema;
    const known = new Set(Object.keys(widgets));
    let dirty = false;

    function walk(node: unknown): unknown {
      if (!node || typeof node !== 'object') return node;
      if (Array.isArray(node)) return node.map(walk);
      const out: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(node as Record<string, unknown>)) {
        if (k === 'ui:widget' && typeof v === 'string' && !known.has(v)) {
          dirty = true;
          if (isDev) {
            consola.error(
              `[JsonSchemaForm] Unknown widget "${v}" — falling back to default. ` +
                `Available: ${[...known].filter((w) => w[0]?.toLowerCase() === w[0]).join(', ')}`,
            );
          }
          continue; // drop unknown widget so RJSF picks the default
        }
        out[k] = walk(v);
      }
      return out;
    }

    const cleaned = walk(uiSchema) as UiSchema | undefined;
    return dirty ? cleaned : uiSchema;
  }, [uiSchema, widgets]);

  // Memoize templates to prevent recreation on every render
  const templates = useMemo(() => ({
    FieldTemplate,
    ObjectFieldTemplate,
    ArrayFieldTemplate,
    ArrayFieldItemTemplate,
    ErrorListTemplate,
    BaseInputTemplate,
  }), []);

  // Memoize callbacks
  const handleSubmit = useCallback((data: IChangeEvent<T>) => {
    if (onSubmit) {
      // Ensure clean data on submit
      const cleanData = {
        ...data,
        formData: normalizeFormData<T>(data.formData, validatedSchema!),
      };
      onSubmit(cleanData);
    }
  }, [onSubmit, validatedSchema]);

  const handleChange = useCallback((data: IChangeEvent<T>) => {
    if (onChange) {
      onChange(data);
    }
  }, [onChange]);

  const handleError = useCallback((errors: RJSFValidationError[]) => {
    if (onError) {
      onError(errors);
    }
  }, [onError]);

  // formContext threads the latest formData + density into widgets/templates so
  // they can react to global form state (conditional disable, density CSS).
  //
  // MUST stay above the invalid-schema early return below — a hook after a
  // conditional return changes the hook count when `validatedSchema` flips
  // (e.g. the caller swaps in a valid schema) and crashes React (#310).
  const formContext = useMemo<JsonFormContext & Record<string, unknown>>(() => ({
    ...(callerFormContext as object | undefined),
    density,
    formData: normalizedFormData,
  }), [callerFormContext, density, normalizedFormData]);

  // Early return if schema is invalid
  if (!validatedSchema) {
    return (
      <div className={className}>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Invalid schema provided. Please check the schema format.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className={className} data-jsonform-density={density}>
      <Form
        schema={validatedSchema}
        uiSchema={safeUiSchema as UiSchema | undefined}
        formData={normalizedFormData}
        validator={validator}
        widgets={widgets}
        templates={templates}
        formContext={formContext}
        onSubmit={handleSubmit}
        onChange={handleChange}
        onError={handleError}
        showErrorList={showErrorList}
        liveValidate={liveValidate}
        disabled={disabled}
        readonly={readonly}
        {...restProps}
      >
        {showSubmitButton && (
          <div className="mt-6 flex gap-2">
            <Button type="submit" disabled={disabled}>
              {submitButtonText}
            </Button>
          </div>
        )}
      </Form>
    </div>
  );
}
