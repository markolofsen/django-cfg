"use client"

import React from 'react';

import { Label } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { FieldTemplateProps } from '@rjsf/utils';

import type { JsonFormDensity } from '../types';

/**
 * Field template for JSON Schema Form
 * Controls the layout and styling of individual form fields
 */
export function FieldTemplate(props: FieldTemplateProps) {
  const {
    id,
    classNames,
    style,
    label,
    help,
    required,
    description,
    errors,
    children,
    displayLabel,
    hidden,
    rawErrors,
  } = props;
  const formContext = (props as { formContext?: { density?: JsonFormDensity } }).formContext;

  if (hidden) {
    return <div className="hidden">{children}</div>;
  }

  const hasError = rawErrors && rawErrors.length > 0;
  const density = (formContext?.density as JsonFormDensity | undefined) ?? 'comfortable';
  const compact = density === 'compact';

  // In compact mode the description is suppressed in the body and forwarded to
  // the label `title=` tooltip — keeps rows dense without losing context.
  const descriptionText =
    typeof description === 'string'
      ? description
      : undefined;
  const labelTitle = compact ? descriptionText : undefined;
  const showDescription = !compact && Boolean(description);

  return (
    <div
      className={cn(compact ? 'space-y-1' : 'space-y-2', classNames)}
      style={style}
    >
      {displayLabel && label && (
        <Label
          htmlFor={id}
          className={cn(
            hasError && 'text-destructive',
            compact && 'text-[10px] font-semibold uppercase tracking-wide text-muted-foreground/70',
          )}
          title={labelTitle}
        >
          {label}
          {required && <span className="text-destructive ml-1">*</span>}
        </Label>
      )}

      {showDescription && (
        <div className="text-sm text-muted-foreground">{description}</div>
      )}

      <div>{children}</div>

      {errors && (
        <div className={compact ? 'text-xs text-destructive' : 'text-sm text-destructive'}>
          {errors}
        </div>
      )}

      {help && !compact && (
        <div className="text-sm text-muted-foreground">{help}</div>
      )}
    </div>
  );
}
