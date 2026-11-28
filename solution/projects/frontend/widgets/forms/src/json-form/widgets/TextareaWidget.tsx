"use client"

import React from 'react';

import type { WidgetProps } from '@rjsf/utils';

import { TextWidget } from './TextWidget';

/**
 * Multiline text widget for JSON Schema Form. Thin wrapper around
 * `TextWidget` that pins `options.widget = 'textarea'` so the
 * underlying renderer reaches the `<textarea>` branch.
 *
 * Registered under the `textarea` ui:widget alias — schemas can opt
 * into multiline editing without setting `ui:options.widget`:
 *
 *     uiSchema = { description: { 'ui:widget': 'textarea' } }
 *
 * Honors all the same `ui:options` as `TextWidget` — most usefully
 * `rows` (default `3`).
 */
export function TextareaWidget(props: WidgetProps) {
  const options = { ...(props.options ?? {}), widget: 'textarea' };
  return <TextWidget {...props} options={options} />;
}
