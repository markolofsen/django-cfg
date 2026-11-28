import { X } from "lucide-react";
import { forwardRef, type ComponentPropsWithoutRef, type ElementRef, type ReactNode } from "react";

import { Button } from "@djangocfg/ui-core/components";
import { cn } from "@djangocfg/ui-core/lib";

/** The heading's look, one for every surface (column, side panel, phone sheet). The caller supplies the element: `h2`, or the dialog's own title. */
export const PANEL_TITLE_CLASS = "truncate font-display text-sm font-(weight:--panel-title-weight) tracking-(--panel-title-tracking) text-(color:--panel-title-color) [text-transform:var(--panel-title-transform)] outline-none";

export interface ChatPanelHeaderProps {
  /** The heading element, styled with `PANEL_TITLE_CLASS`. */
  readonly heading: ReactNode;
  /** What the thread is about, under the heading. */
  readonly description?: ReactNode;
  /** Controls before the close button (new chat, sessions). */
  readonly actions?: ReactNode;
  /** The close control: `<PanelCloseButton />`, or wrapped in the surface's own close part. */
  readonly close: ReactNode;
  readonly className?: string;
}

/**
 * The one header of a chat surface. A wide column, a tablet side panel and a phone sheet all draw it, so the title, the controls and Close are in the same
 * places at every width: title at the left; at the right the actions, a thin divider, then Close. The divider keeps Close from reading as one more action.
 */
export function ChatPanelHeader({ heading, description, actions, close, className }: ChatPanelHeaderProps) {
  return (
    // The right padding is the vertical gap around the 2rem Close button, so the button sits the same distance from the top, the bottom and the right edge.
    // A fixed height, `--panel-header-h` (3rem): a host gives its own page header the same value, so the two hairlines meet on one horizontal line.
    <header className={cn("box-border flex h-[var(--panel-header-h,3rem)] shrink-0 items-center justify-between gap-3 border-b ps-4 pe-[calc((var(--panel-header-h,3rem)-2rem)/2)]", className)}>
      <div className="min-w-0">
        {heading}
        {description ? <div className="truncate text-xs text-muted-foreground">{description}</div> : null}
      </div>
      <div className="flex shrink-0 items-center gap-1">
        {actions ? (
          <>
            {actions}
            <span className="mx-1 h-4 w-px bg-border" aria-hidden="true" />
          </>
        ) : null}
        {close}
      </div>
    </header>
  );
}

export interface PanelIconButtonProps extends Omit<ComponentPropsWithoutRef<typeof Button>, "children" | "size" | "variant"> {
  /** Accessible name and tooltip text. */
  readonly label: string;
  /** A `useHotkey` string shown after the label in the tooltip for the viewer's system (`mod+j`). */
  readonly hotkey?: string;
  /** The glyph, drawn at `size-4`. */
  readonly children: ReactNode;
}

/**
 * The one icon control of a chat header: a stock UI Core icon `Button` (square corners), ghost, `size-4` glyph, and the same tooltip everywhere (`Button`'s `tooltip` prop: the label, then the key in a muted tone). Help, the "..." menu, new chat,
 * sessions and Close are all this, so they cannot drift apart. It forwards its ref and props, so it works as the child of a trigger (`PopoverTrigger asChild`, `DialogClose asChild`).
 */
export const PanelIconButton = forwardRef<ElementRef<typeof Button>, PanelIconButtonProps>(({ label, hotkey, className, children, ...props }, ref) => (
  <Button ref={ref} type="button" variant="ghost" size="icon" aria-label={label} tooltip={{ content: label, hotkey }} className={className} {...props}>
    {children}
  </Button>
));
PanelIconButton.displayName = "PanelIconButton";

/** The close button every surface uses (an `X`, the same round control as the actions). Pass `onClick`, or wrap it in a close part with `asChild`. */
export const PanelCloseButton = forwardRef<ElementRef<typeof Button>, Omit<PanelIconButtonProps, "children">>((props, ref) => (
  <PanelIconButton ref={ref} {...props}>
    <X className="size-4" aria-hidden="true" />
  </PanelIconButton>
));
PanelCloseButton.displayName = "PanelCloseButton";
