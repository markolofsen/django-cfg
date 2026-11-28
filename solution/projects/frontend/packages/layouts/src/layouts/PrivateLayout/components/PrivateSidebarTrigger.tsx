/**
 * The one sidebar button: same box, icon and position rules on mobile and desktop.
 * In the top bar it opens the sidebar; inside the sidebar header it closes or collapses it. Both are
 * `toggleSidebar`. No tooltip and no native title (decided 2026-11-04, `87a7b8019`): the icon is familiar and a hover
 * card over it got in the way. `aria-label` names the action; Cmd/Ctrl+B still works through ui-core's sidebar
 * provider. The labels are plain English: the layouts have no message catalogue (only a locale hook).
 */

'use client';

import React from 'react';
import { PanelLeft } from 'lucide-react';

import { Button, useSidebar } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { TRIGGER_CLASS } from '../geometry';

export const PrivateSidebarTrigger = React.forwardRef<
  React.ElementRef<typeof Button>,
  React.ComponentProps<typeof Button>
>(({ className, onClick, ...props }, ref) => {
  const { toggleSidebar, isMobile, openMobile, open } = useSidebar();
  const isOpen = isMobile ? openMobile : open;
  const label = isOpen ? 'Close sidebar' : 'Open sidebar';

  return (
    <Button
      ref={ref}
      type="button"
      data-sidebar="trigger"
      variant="ghost"
      size="icon"
      aria-label={label}
      className={cn(TRIGGER_CLASS, className)}
      onClick={(event) => {
        onClick?.(event);
        toggleSidebar();
      }}
      {...props}
    >
      <PanelLeft aria-hidden />
    </Button>
  );
});
PrivateSidebarTrigger.displayName = 'PrivateSidebarTrigger';
