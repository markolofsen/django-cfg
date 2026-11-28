'use client';

import { useState } from 'react';
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuTrigger,
} from '@djangocfg/ui-core/components';

import type {
  TreeContextMenuItem,
  TreeRowRenderProps,
} from '../../types';

interface RowContextMenuProps<T> {
  rowProps: TreeRowRenderProps<T>;
  items: TreeContextMenuItem<T>[];
  trigger: React.ReactNode;
}

/**
 * Per-row context menu.
 *
 * PERF: every visible row wraps its trigger in a `<ContextMenu>`, so a
 * large tree mounts hundreds of these. Building the full
 * `<ContextMenuContent>` item subtree for each of them on every render is
 * what made right-click feel laggy (the selection change on right-click
 * re-renders all rows, each rebuilding its menu body). We now render the
 * content body ONLY while this row's menu is actually open — closed rows
 * cost just the lightweight `ContextMenu` + `Trigger` shell.
 */
function RowContextMenu<T>({
  rowProps,
  items,
  trigger,
}: RowContextMenuProps<T>) {
  const [open, setOpen] = useState(false);
  return (
    <ContextMenu onOpenChange={setOpen}>
      <ContextMenuTrigger asChild>{trigger}</ContextMenuTrigger>
      {open ? (
        <ContextMenuContent>
          {items.map((item, idx) => {
            if (item === 'separator') {
              return <ContextMenuSeparator key={`sep-${idx}`} />;
            }
            const Icon = item.icon;
            return (
              <ContextMenuItem
                key={item.id}
                disabled={item.disabled}
                variant={item.destructive ? 'destructive' : undefined}
                onSelect={() => item.onSelect(rowProps)}
              >
                {Icon ? <Icon /> : null}
                {item.label}
                {item.shortcut ? (
                  <ContextMenuShortcut>{item.shortcut}</ContextMenuShortcut>
                ) : null}
              </ContextMenuItem>
            );
          })}
        </ContextMenuContent>
      ) : null}
    </ContextMenu>
  );
}

/**
 * Render an array of declarative menu items as a themed `<ContextMenu>`
 * wrapped around the supplied trigger element. Pure presentational layer
 * — the caller resolves and merges items.
 */
export function renderItemsAsContextMenu<T>(
  rowProps: TreeRowRenderProps<T>,
  items: TreeContextMenuItem<T>[],
  trigger: React.ReactNode,
): React.ReactNode {
  return <RowContextMenu rowProps={rowProps} items={items} trigger={trigger} />;
}

/**
 * Drop trailing / leading / duplicate separators so a merged menu never
 * shows a separator next to a section header or another separator.
 */
export function tidyMenuItems<T>(
  items: TreeContextMenuItem<T>[],
): TreeContextMenuItem<T>[] {
  const out: TreeContextMenuItem<T>[] = [];
  for (const it of items) {
    if (it === 'separator') {
      if (out.length === 0) continue;
      if (out[out.length - 1] === 'separator') continue;
      out.push(it);
    } else {
      out.push(it);
    }
  }
  while (out.length > 0 && out[out.length - 1] === 'separator') out.pop();
  return out;
}
