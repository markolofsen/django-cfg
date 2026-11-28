"use client"

import { ChevronDown, ChevronRight } from 'lucide-react';
import React, { useState } from 'react';

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { ObjectFieldTemplateProps } from '@rjsf/utils';

import type { JsonFormDensity, UiGroup } from '../types';

/**
 * Static map of literal grid-column classes.
 *
 * Tailwind JIT only compiles classes it can see at build time, so a
 * runtime-built `grid-cols-${n}` string is never emitted. Listing the
 * full literal classes here keeps `ui:grid` working. Columns collapse
 * to a single column on small screens for responsive behaviour.
 */
const GRID_COL_CLASS: Record<number, string> = {
  1: 'grid-cols-1',
  2: 'grid-cols-1 sm:grid-cols-2',
  3: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3',
  4: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-4',
};

/**
 * Object field template for JSON Schema Form
 *
 * Supports:
 * - Collapsible groups via ui:collapsible option
 * - Grid layout via ui:grid option
 * - Custom styling via ui:className
 *
 * Usage in uiSchema:
 * ```json
 * {
 *   "colors": {
 *     "ui:collapsible": true,
 *     "ui:collapsed": false,
 *     "ui:grid": 2
 *   }
 * }
 * ```
 */
export function ObjectFieldTemplate(props: ObjectFieldTemplateProps) {
  const {
    title,
    description,
    properties,
    required,
    uiSchema,
  } = props;
  const formContext = (props as { formContext?: { density?: JsonFormDensity } }).formContext;

  // UI options
  const isCollapsible = uiSchema?.['ui:collapsible'] === true;
  const defaultCollapsed = uiSchema?.['ui:collapsed'] === true;
  const gridCols = uiSchema?.['ui:grid'] as number | undefined;
  const className = uiSchema?.['ui:className'] as string | undefined;
  const uiGroups = uiSchema?.['ui:groups'] as readonly UiGroup[] | undefined;
  const density = (formContext?.density as JsonFormDensity | undefined) ?? 'comfortable';
  const compact = density === 'compact';

  // Collapsible state
  const [isOpen, setIsOpen] = useState(!defaultCollapsed);

  // Check if this is root object (no title usually means root)
  const isRoot = !title;

  // Grid class based on columns. `ui:grid` is clamped to the 1-4 range
  // covered by GRID_COL_CLASS so Tailwind always has a literal class.
  const colClass =
    typeof gridCols === 'number'
      ? GRID_COL_CLASS[Math.min(4, Math.max(1, Math.round(gridCols)))]
      : undefined;
  const gridClass = colClass
    ? cn('grid', compact ? 'gap-2' : 'gap-4', colClass)
    : compact
      ? 'space-y-2'
      : 'space-y-4';

  // When `ui:groups` is specified, render listed fields inside collapsible
  // sub-sections; remaining (ungrouped) fields render flat above the groups.
  const groupedContent = uiGroups
    ? renderUiGroups({ properties, uiGroups, gridClass, className, compact })
    : null;

  // Content wrapper
  const content = groupedContent ?? (
    <div className={cn(gridClass, className)}>
      {properties.map((element) => (
        <div key={element.name} className="property-wrapper">
          {element.content}
        </div>
      ))}
    </div>
  );

  // Root object - no wrapper
  if (isRoot) {
    return <div className="space-y-6">{content}</div>;
  }

  // Collapsible group
  if (isCollapsible) {
    return (
      <Collapsible open={isOpen} onOpenChange={setIsOpen} className="space-y-2">
        <CollapsibleTrigger className="flex w-full items-center justify-between rounded-lg border bg-muted/50 px-4 py-3 text-left hover:bg-muted transition-colors">
          <div>
            <h3 className="text-sm font-semibold">
              {title}
              {required && <span className="text-destructive ml-1">*</span>}
            </h3>
            {description && (
              <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
            )}
          </div>
          <ChevronDown
            className={cn(
              'h-4 w-4 text-muted-foreground transition-transform duration-200',
              isOpen && 'rotate-180'
            )}
          />
        </CollapsibleTrigger>
        <CollapsibleContent className="pl-1 pr-1 pt-2">
          {content}
        </CollapsibleContent>
      </Collapsible>
    );
  }

  // Regular group with title
  return (
    <div className="space-y-4">
      {title && (
        <div className="border-b pb-2">
          <h3 className="text-sm font-semibold">
            {title}
            {required && <span className="text-destructive ml-1">*</span>}
          </h3>
          {description && (
            <p className="text-xs text-muted-foreground mt-1">{description}</p>
          )}
        </div>
      )}
      {content}
    </div>
  );
}

interface RenderUiGroupsOptions {
  properties: ObjectFieldTemplateProps['properties'];
  uiGroups: readonly UiGroup[];
  gridClass: string;
  className?: string;
  compact: boolean;
}

function renderUiGroups({
  properties,
  uiGroups,
  gridClass,
  className,
  compact,
}: RenderUiGroupsOptions) {
  const propsByName = new Map(properties.map((p) => [p.name, p]));
  const groupedFieldNames = new Set(uiGroups.flatMap((g) => g.fields));
  // Fields not listed in any group render flat above the groups.
  const ungrouped = properties.filter((p) => !groupedFieldNames.has(p.name));

  return (
    <div className={cn(compact ? 'space-y-2' : 'space-y-3', className)}>
      {ungrouped.length > 0 ? (
        <div className={gridClass}>
          {ungrouped.map((element) => (
            <div key={element.name} className="property-wrapper">
              {element.content}
            </div>
          ))}
        </div>
      ) : null}

      {uiGroups.map((group) => {
        const groupProps = group.fields
          .map((name) => propsByName.get(name))
          .filter((p): p is ObjectFieldTemplateProps['properties'][number] => Boolean(p));
        if (groupProps.length === 0) return null;
        return (
          <UiGroupSection
            key={group.title}
            group={group}
            gridClass={gridClass}
            compact={compact}
          >
            {groupProps.map((element) => (
              <div key={element.name} className="property-wrapper">
                {element.content}
              </div>
            ))}
          </UiGroupSection>
        );
      })}
    </div>
  );
}

interface UiGroupSectionProps {
  group: UiGroup;
  gridClass: string;
  compact: boolean;
  children: React.ReactNode;
}

function UiGroupSection({ group, gridClass, compact, children }: UiGroupSectionProps) {
  const [open, setOpen] = useState(group.defaultOpen ?? true);
  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <CollapsibleTrigger
        className={cn(
          'flex w-full items-center gap-1.5 py-1 transition-colors hover:text-foreground',
          compact
            ? 'text-[10px] font-semibold uppercase tracking-wide text-muted-foreground/70'
            : 'text-xs font-semibold uppercase tracking-wide text-muted-foreground',
        )}
      >
        <ChevronRight
          className={cn(
            'h-3 w-3 shrink-0 transition-transform duration-200',
            open && 'rotate-90',
          )}
          aria-hidden
        />
        <span>{group.title}</span>
      </CollapsibleTrigger>
      <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down">
        <div className={cn('border-l border-border/40 pl-3 pb-2 pt-1', gridClass)}>
          {children}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
