"use client"

import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';
import { ArrayFieldItemTemplateProps, getTemplate, getUiOptions } from '@rjsf/utils';

/**
 * Array field item template for JSON Schema Form
 * Renders individual array items with proper styling and action buttons
 *
 * In RJSF v6, this template is responsible for rendering each item in an array,
 * including the item content (children) and the action buttons (remove, move up/down, copy).
 */
export function ArrayFieldItemTemplate(props: ArrayFieldItemTemplateProps) {
  const {
    children,
    className,
    buttonsProps,
    hasToolbar,
    registry,
    uiSchema,
  } = props;

  const uiOptions = getUiOptions(uiSchema);
  const ArrayFieldItemButtonsTemplate = getTemplate(
    'ArrayFieldItemButtonsTemplate',
    registry,
    uiOptions,
  );

  return (
    <div
      className={cn(
        'flex gap-2 items-start p-4 rounded-md border bg-card',
        className
      )}
    >
      <div className="flex-1">{children}</div>
      {hasToolbar && (
        <div className="flex items-center gap-1">
          <ArrayFieldItemButtonsTemplate {...buttonsProps} />
        </div>
      )}
    </div>
  );
}
