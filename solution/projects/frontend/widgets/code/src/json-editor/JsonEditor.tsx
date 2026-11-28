'use client';

/**
 * JsonEditor — editable JSON tree.
 *
 * Thin wrapper over `json-edit-react` (MIT, CarlosNZ). The library
 * handles the hard parts (inline editing, drag-reorder, JSON-Schema
 * validation, undo/redo, keyboard nav, copy-to-clipboard) — we apply
 * our theme tokens and a sane default surface, nothing more.
 *
 * When to use:
 *   - User is *editing* JSON live (debug Store panel, config UI).
 *   - You need schema validation or controlled mutations with
 *     `onUpdate`.
 *
 * When NOT to use:
 *   - Read-only display → use `@djangocfg/widget-data/json-tree` (≈ 10×
 *     lighter bundle, search + copy-path included).
 */

import { JsonEditor as RawEditor, type JsonEditorProps as RawProps } from 'json-edit-react';
import { useMemo } from 'react';
import { useResolvedTheme } from '@djangocfg/ui-core/hooks';
import { cn } from '@djangocfg/ui-core/lib';

export interface JsonEditorProps extends Omit<RawProps, 'theme'> {
  /** Extra class on the root container. */
  className?: string;
  /**
   * Hide chrome the host already provides. When `false`, no border /
   * background — the editor sits flush in the surrounding pane.
   * Default `true`.
   */
  bordered?: boolean;
}

/**
 * Hand-rolled theme bridge: maps our semantic CSS vars onto
 * json-edit-react's theme slots. Light/dark resolution lives in our
 * `useResolvedTheme`; the library only sees concrete colours.
 *
 * We keep this minimal — most slots inherit `currentColor`, only the
 * data-typed tokens get explicit Tailwind palette values so the
 * keys/strings/numbers stay legible on every host surface.
 */
function useEditorTheme(): RawProps['theme'] {
  const resolved = useResolvedTheme();
  return useMemo(
    () => ({
      displayName: 'djangocfg',
      styles: {
        container: {
          backgroundColor: 'transparent',
          fontFamily:
            "'SF Mono', ui-monospace, 'JetBrains Mono', Menlo, Consolas, monospace",
          fontSize: '12px',
        },
        property:
          resolved === 'dark' ? 'rgb(167 139 250)' : 'rgb(124 58 237)', // violet-400 / violet-600
        bracket:
          resolved === 'dark' ? 'rgb(148 163 184)' : 'rgb(100 116 139)', // slate-400 / slate-500
        itemCount:
          resolved === 'dark' ? 'rgb(100 116 139)' : 'rgb(148 163 184)',
        string:
          resolved === 'dark' ? 'rgb(52 211 153)' : 'rgb(5 150 105)', // emerald-400 / emerald-600
        number:
          resolved === 'dark' ? 'rgb(56 189 248)' : 'rgb(2 132 199)', // sky-400 / sky-600
        boolean:
          resolved === 'dark' ? 'rgb(251 191 36)' : 'rgb(217 119 6)', // amber-400 / amber-600
        null: {
          color: resolved === 'dark' ? 'rgb(100 116 139)' : 'rgb(148 163 184)',
          fontStyle: 'italic',
        },
        input: {
          backgroundColor:
            resolved === 'dark' ? 'rgb(30 41 59)' : 'rgb(241 245 249)',
          color: resolved === 'dark' ? 'white' : 'rgb(15 23 42)',
          borderRadius: 4,
          padding: '2px 6px',
        },
        inputHighlight:
          resolved === 'dark' ? 'rgba(96, 165, 250, 0.25)' : 'rgba(59, 130, 246, 0.15)',
        iconCollection:
          resolved === 'dark' ? 'rgb(148 163 184)' : 'rgb(100 116 139)',
        iconEdit: 'currentColor',
        iconDelete: 'rgb(239 68 68)',
        iconAdd: 'rgb(34 197 94)',
        iconCopy: 'currentColor',
        iconOk: 'rgb(34 197 94)',
        iconCancel: 'rgb(239 68 68)',
      },
    }),
    [resolved],
  );
}

export function JsonEditor({
  className,
  bordered = true,
  ...props
}: JsonEditorProps) {
  const theme = useEditorTheme();
  return (
    <div
      className={cn(
        'json-editor-host w-full',
        bordered &&
          'overflow-hidden rounded-md border border-border/60 bg-card px-3 py-2',
        className,
      )}
    >
      <RawEditor theme={theme} {...props} />
    </div>
  );
}
