/**
 * Peek panel: the full sidebar floated over the page while it is collapsed.
 * Opened by hover intent on the left screen edge strip (the toggle button itself does not open it), held by `SidebarPeekProvider`,
 * slides in and out (it stays mounted while the exit animation runs).
 */

'use client';

import React from 'react';

import { useSidebarPeek } from '../hooks';
import { SidebarBody } from './SidebarBody';
import { SidebarResizeHandle } from './SidebarResizeHandle';

export function SidebarPeek() {
  const peek = useSidebarPeek();
  if (!peek) return null;

  return (
    <>
      {peek.hoverEnabled ? (
        // Thin hot strip on the left edge: resting the pointer here opens the panel.
        <div
          data-sidebar="peek-edge"
          aria-hidden
          className="fixed inset-y-0 left-0 z-40 w-1.5"
          {...peek.zoneProps}
        />
      ) : null}
      {peek.mounted ? (
        <div
          data-sidebar="peek"
          data-state={peek.state}
          role="complementary"
          aria-label="Navigation"
          inert={peek.state === 'closed'}
          {...peek.panelProps}
          className={[
            'private-sidebar-peek fixed bottom-2 left-2 top-2 z-50 flex w-(--sidebar-width) flex-col overflow-hidden',
            'rounded-xl border border-sidebar-border bg-sidebar text-sidebar-foreground shadow-2xl',
          ].join(' ')}
        >
          <SidebarBody />
          <SidebarResizeHandle />
        </div>
      ) : null}
    </>
  );
}
