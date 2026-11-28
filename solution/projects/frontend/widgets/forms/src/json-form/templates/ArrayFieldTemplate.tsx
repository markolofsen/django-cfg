"use client"

import { Plus } from 'lucide-react';
import React from 'react';

import { Button } from '@djangocfg/ui-core/components';
import { useAppT } from '@djangocfg/i18n';
import { ArrayFieldTemplateProps } from '@rjsf/utils';

/**
 * Array field template for JSON Schema Form
 * Renders array items with add/remove controls
 *
 * NOTE: In RJSF v6, `items` is an array of ReactElement (already rendered),
 * NOT an array of objects with {children, hasRemove, etc.}.
 * The actual rendering of each item (including remove buttons) is handled
 * by ArrayFieldItemTemplate.
 */
export function ArrayFieldTemplate(props: ArrayFieldTemplateProps) {
  const {
    title,
    items,
    canAdd,
    onAddClick,
    required,
  } = props;
  const t = useAppT();

  return (
    <div className="space-y-4">
      {title && (
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">
            {title}
            {required && <span className="text-destructive ml-1">*</span>}
          </h3>
          {canAdd && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onAddClick}
              className="gap-2"
            >
              <Plus className="h-4 w-4" />
              {t('tools.jsonForm.addItem')}
            </Button>
          )}
        </div>
      )}

      {/* In RJSF v6, items is already an array of ReactElements */}
      <div className="space-y-3">
        {items}
      </div>

      {items.length === 0 && (
        <div className="text-center py-8 text-muted-foreground border-2 border-dashed rounded-md">
          {t('tools.jsonForm.noItems')}
          {canAdd && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={onAddClick}
              className="mt-2 gap-2"
            >
              <Plus className="h-4 w-4" />
              {t('tools.jsonForm.addFirstItem')}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
