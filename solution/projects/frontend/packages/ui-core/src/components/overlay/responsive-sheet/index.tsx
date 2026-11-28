"use client"

/**
 * Responsive Sheet
 *
 * Dialog on desktop, Drawer (pull-down) on mobile.
 * Automatically switches based on screen width using useIsMobile hook.
 */

import * as React from 'react';

import { useIsMobile } from '../../../hooks';
import { cn } from '../../../lib/utils';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../../overlay/dialog';

import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from '../../overlay/drawer';

// ─────────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────────

const ResponsiveSheetContext = React.createContext<{ isMobile: boolean }>({
  isMobile: false,
});

// ─────────────────────────────────────────────────────────────────────────────
// Root
// ─────────────────────────────────────────────────────────────────────────────

interface ResponsiveSheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

function ResponsiveSheet({ open, onOpenChange, children }: ResponsiveSheetProps) {
  const isMobile = useIsMobile();

  if (isMobile) {
    return (
      <ResponsiveSheetContext.Provider value={{ isMobile: true }}>
        <Drawer open={open} onOpenChange={onOpenChange}>
          {children}
        </Drawer>
      </ResponsiveSheetContext.Provider>
    );
  }

  return (
    <ResponsiveSheetContext.Provider value={{ isMobile: false }}>
      <Dialog open={open} onOpenChange={onOpenChange}>
        {children}
      </Dialog>
    </ResponsiveSheetContext.Provider>
  );
}
ResponsiveSheet.displayName = "ResponsiveSheet"

// ─────────────────────────────────────────────────────────────────────────────
// Content
// ─────────────────────────────────────────────────────────────────────────────

/** Reading width of the panel. `md` suits a form or a detail card. */
type ResponsiveSheetWidth = "sm" | "md" | "lg" | "xl";

const WIDTH: Record<ResponsiveSheetWidth, string> = {
  sm: "sm:max-w-sm",
  md: "sm:max-w-md",
  lg: "sm:max-w-lg",
  xl: "sm:max-w-xl",
};

interface ResponsiveSheetContentProps {
  children: React.ReactNode;
  className?: string;
  /** Panel width on a wide viewport. A phone always takes the full width. */
  width?: ResponsiveSheetWidth;
  /**
   * Cap the panel at the viewport and scroll its body. Default.
   *
   * `false` for a panel that lays out its own scrolling regions — a header and
   * footer that must stay put around a scrolling middle. It then owns the cap
   * too; without one the overflow returns.
   */
  scroll?: boolean;
}

/**
 * The panel.
 *
 * It arrives sized, inset and centred — a caller passes CONTENT, not a layout.
 * Every default here exists because a caller had to supply it by hand and the
 * two callers we had disagreed: the same `w-[calc(100%-1rem)]` twice, one of
 * them with a `flex flex-col` that made a short card stand full height.
 *
 * The phone case is where this matters. `DialogContent` carries its own
 * padding and centring; `DrawerContent` does not, so anything that renders as
 * both lost its layout at the breakpoint and nowhere else.
 *
 * HEIGHT is a default here for the same reason width is. The desktop
 * `DialogContent` is `fixed` and centred by `-translate-y-1/2` with no cap, so
 * content taller than the viewport overflows BOTH edges — the top scrolls out
 * of reach, and nothing clips, so nothing scrolls. Every caller that got this
 * right passed the same `max-h-[85vh]` by hand; the one that forgot lost its
 * header off the top. A caller that wants its own scrolling regions passes
 * `scroll={false}` and owns the cap.
 */
function ResponsiveSheetContent({
  children,
  className,
  width = "md",
  scroll = true,
}: ResponsiveSheetContentProps) {
  const { isMobile } = React.useContext(ResponsiveSheetContext);

  if (isMobile) {
    // `height="auto"` hugs the content; the drawer's own `max-h` is the
    // ceiling. A cap passed from here would become a fixed height instead,
    // because the panel is a flex column and fills what it is given.
    return (
      <DrawerContent className={className} height="auto">
        {children}
      </DrawerContent>
    );
  }

  // The cap sits on the panel and the scroll on an inner box, never both on
  // one element: `DialogContent` is a grid, and a scrollport that is also the
  // grid would clip the close button pinned to its corner.
  if (!scroll) {
    return (
      <DialogContent className={cn("w-[calc(100%-1rem)]", WIDTH[width], className)}>
        {children}
      </DialogContent>
    );
  }

  return (
    <DialogContent
      className={cn(
        "max-h-[85dvh] w-[calc(100%-1rem)] grid-rows-[minmax(0,1fr)] overflow-hidden",
        WIDTH[width],
        className,
      )}
    >
      <div className="min-h-0 overflow-y-auto overscroll-contain">{children}</div>
    </DialogContent>
  );
}
ResponsiveSheetContent.displayName = "ResponsiveSheetContent"

// ─────────────────────────────────────────────────────────────────────────────
// Header
// ─────────────────────────────────────────────────────────────────────────────

type ResponsiveSheetHeaderProps = React.HTMLAttributes<HTMLDivElement>;

function ResponsiveSheetHeader({ className, ...props }: ResponsiveSheetHeaderProps) {
  const { isMobile } = React.useContext(ResponsiveSheetContext);

  if (isMobile) {
    return <DrawerHeader className={className} {...props} />;
  }

  return <DialogHeader className={className} {...props} />;
}
ResponsiveSheetHeader.displayName = "ResponsiveSheetHeader"

// ─────────────────────────────────────────────────────────────────────────────
// Title
// ─────────────────────────────────────────────────────────────────────────────

type ResponsiveSheetTitleProps = React.HTMLAttributes<HTMLHeadingElement>;

function ResponsiveSheetTitle({ className, ...props }: ResponsiveSheetTitleProps) {
  const { isMobile } = React.useContext(ResponsiveSheetContext);

  if (isMobile) {
    return <DrawerTitle className={className} {...props} />;
  }

  return <DialogTitle className={className} {...props} />;
}
ResponsiveSheetTitle.displayName = "ResponsiveSheetTitle"

// ─────────────────────────────────────────────────────────────────────────────
// Description
// ─────────────────────────────────────────────────────────────────────────────

type ResponsiveSheetDescriptionProps = React.HTMLAttributes<HTMLParagraphElement>;

function ResponsiveSheetDescription({ className, ...props }: ResponsiveSheetDescriptionProps) {
  const { isMobile } = React.useContext(ResponsiveSheetContext);

  if (isMobile) {
    return <DrawerDescription className={className} {...props} />;
  }

  return <DialogDescription className={className} {...props} />;
}
ResponsiveSheetDescription.displayName = "ResponsiveSheetDescription"

// ─────────────────────────────────────────────────────────────────────────────
// Footer
// ─────────────────────────────────────────────────────────────────────────────

type ResponsiveSheetFooterProps = React.HTMLAttributes<HTMLDivElement>;

function ResponsiveSheetFooter({ className, ...props }: ResponsiveSheetFooterProps) {
  const { isMobile } = React.useContext(ResponsiveSheetContext);

  if (isMobile) {
    return <DrawerFooter className={className} {...props} />;
  }

  return <DialogFooter className={className} {...props} />;
}
ResponsiveSheetFooter.displayName = "ResponsiveSheetFooter"

// ─────────────────────────────────────────────────────────────────────────────
// Exports
// ─────────────────────────────────────────────────────────────────────────────

export {
  ResponsiveSheet,
  ResponsiveSheetContent,
  ResponsiveSheetHeader,
  ResponsiveSheetTitle,
  ResponsiveSheetDescription,
  ResponsiveSheetFooter,
};
