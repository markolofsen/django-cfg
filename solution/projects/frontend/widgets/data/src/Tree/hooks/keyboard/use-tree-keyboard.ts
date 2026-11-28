'use client';

import { useCallback, useRef } from 'react';
import { useHotkey } from '@djangocfg/ui-core/hooks';

import { edgeRowId, nextRowId, prevRowId } from './arrow-nav';
import { resolveLeftArrow, resolveRightArrow } from './expand-collapse';
import { resolveActivate } from './activation';
import type {
  CurrentRow,
  UseTreeKeyboardOptions,
  UseTreeKeyboardReturn,
} from './types';

/**
 * Standard tree keyboard navigation, scoped to the container ref.
 *
 *   - ↑ / ↓          : prev / next visible row (Shift extends range)
 *   - Home / End     : first / last visible row (Shift extends range)
 *   - → / ←          : expand-or-jump-to-child / collapse-or-jump-to-parent
 *   - Enter / Space  : activate (folder → toggle, leaf → onActivate)
 *   - Esc            : clear selection
 *   - Cmd/Ctrl + A   : select all (multi-select only)
 *
 * Pure decision-making lives in the sibling helpers (`arrow-nav.ts`,
 * `expand-collapse.ts`, `activation.ts`) so it's unit-testable without
 * a DOM. This file only wires up `useHotkey` bindings and dispatches
 * the helper outcomes back to the consumer's callbacks.
 */
export function useTreeKeyboard<T>({
  rows,
  focusedId,
  enabled = true,
  multiSelect = false,
  onFocus,
  onSelect,
  onActivate,
  onExpand,
  onCollapse,
  onClearSelection,
  onSelectAll,
}: UseTreeKeyboardOptions<T>): UseTreeKeyboardReturn {
  // Keep latest values in refs so the callbacks below stay stable across
  // renders — react-hotkeys-hook re-binds on dep change otherwise.
  const rowsRef = useRef(rows);
  const focusedIdRef = useRef(focusedId);
  rowsRef.current = rows;
  focusedIdRef.current = focusedId;

  const getCurrent = (): CurrentRow<T> => {
    const r = rowsRef.current;
    const id = focusedIdRef.current;
    const idx = id ? r.findIndex((x) => x.node.id === id) : -1;
    return { rows: r, idx, current: (idx >= 0 ? r[idx] : null) ?? null };
  };

  // Down / Shift+Down. Plain moves focus, shift extends selection range.
  const refDown = useHotkey(
    ['down', 'shift+down'],
    (e) => {
      const { rows: r, idx } = getCurrent();
      const id = nextRowId(r, idx);
      if (id) onFocus(id, { extend: multiSelect && e.shiftKey });
    },
    { enabled, preventDefault: true, description: 'Next row (Shift extends)' },
  );

  const refUp = useHotkey(
    ['up', 'shift+up'],
    (e) => {
      const { rows: r, idx } = getCurrent();
      const id = prevRowId(r, idx);
      if (id) onFocus(id, { extend: multiSelect && e.shiftKey });
    },
    { enabled, preventDefault: true, description: 'Previous row (Shift extends)' },
  );

  const refHome = useHotkey(
    ['home', 'shift+home'],
    (e) => {
      const id = edgeRowId(rowsRef.current, 'first');
      if (id) onFocus(id, { extend: multiSelect && e.shiftKey });
    },
    { enabled, preventDefault: true, description: 'First row (Shift extends)' },
  );

  const refEnd = useHotkey(
    ['end', 'shift+end'],
    (e) => {
      const id = edgeRowId(rowsRef.current, 'last');
      if (id) onFocus(id, { extend: multiSelect && e.shiftKey });
    },
    { enabled, preventDefault: true, description: 'Last row (Shift extends)' },
  );

  const refSelectAll = useHotkey(
    'mod+a',
    () => {
      if (!multiSelect) return;
      onSelectAll?.();
    },
    {
      enabled: enabled && multiSelect,
      preventDefault: true,
      description: 'Select all visible rows',
    },
  );

  const refRight = useHotkey(
    'right',
    () => {
      const { rows: r, idx, current } = getCurrent();
      const out = resolveRightArrow(current, r, idx);
      switch (out.kind) {
        case 'expand':
          onExpand(out.id);
          return;
        case 'focus':
          onFocus(out.id, { extend: false });
          return;
        case 'noop':
          return;
      }
    },
    { enabled, preventDefault: true, description: 'Expand / first child' },
  );

  const refLeft = useHotkey(
    'left',
    () => {
      const { current } = getCurrent();
      const out = resolveLeftArrow(current);
      switch (out.kind) {
        case 'collapse':
          onCollapse(out.id);
          return;
        case 'focus':
          onFocus(out.id, { extend: false });
          return;
        case 'noop':
          return;
      }
    },
    { enabled, preventDefault: true, description: 'Collapse / parent' },
  );

  const refActivate = useHotkey(
    ['enter', 'space'],
    () => {
      const { current } = getCurrent();
      const out = resolveActivate(current);
      if (out.kind === 'noop') return;
      onSelect(out.kind === 'activate-leaf' ? out.id : out.id);
      if (out.kind === 'toggle-folder') {
        if (out.willExpand) onExpand(out.id);
        else onCollapse(out.id);
      } else {
        onActivate(out.id);
      }
    },
    { enabled, preventDefault: true, description: 'Activate / toggle' },
  );

  const refEscape = useHotkey(
    'escape',
    () => onClearSelection(),
    { enabled, preventDefault: true, description: 'Clear selection' },
  );

  const ref = useCallback(
    (instance: HTMLElement | null) => {
      refDown(instance);
      refUp(instance);
      refHome(instance);
      refEnd(instance);
      refRight(instance);
      refLeft(instance);
      refActivate(instance);
      refEscape(instance);
      refSelectAll(instance);
    },
    [
      refDown,
      refUp,
      refHome,
      refEnd,
      refRight,
      refLeft,
      refActivate,
      refEscape,
      refSelectAll,
    ],
  );

  return { ref };
}
