import { useCallback, useRef, type ReactNode } from "react";

import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@djangocfg/ui-core/components";

import { ChatPanelHeader, PANEL_TITLE_CLASS, PanelCloseButton } from "./panel-header";
import { useLayer, useViewportBox, type UseLayerOptions } from "../../primitives";

export interface ChatSheetProps {
  readonly open: boolean;
  readonly onOpenChange: (open: boolean) => void;
  /** The heading, and the dialog's accessible name. */
  readonly title: string;
  /** Replaces the visible heading (a segment control, a count beside the title). The title stays the dialog's accessible name, hidden. */
  readonly heading?: ReactNode;
  /** What the thread is about, under the title. */
  readonly description?: string;
  /** Accessible name of the close button. Default "Close". */
  readonly closeLabel?: string;
  /** Controls in the header, before the close button (a "more" menu, for one). */
  readonly actions?: ReactNode;
  /** The `<Chat>` (or the host's own column). */
  readonly children: ReactNode;
  /**
   * Opt-outs. Everything is ON by default; the host passes nothing.
   * `viewport`: size the layer from `visualViewport` (keyboard, pan, safe areas).
   * `back`: the phone's Back closes it.
   * `inert`: the page behind is inert. `appRoot` names the page root (selector, element or function); absent, the `[data-app-root]` element, else every other child of `<body>`.
   * `lockScroll`: page scroll is locked without a layout shift.
   * `autoFocus`: focus the field on open (off on phones: it would raise the keyboard over the answer).
   */
  readonly behaviour?: {
    readonly viewport?: boolean;
    readonly back?: boolean;
    readonly inert?: boolean;
    readonly appRoot?: UseLayerOptions["appRoot"];
    readonly lockScroll?: boolean;
    readonly autoFocus?: boolean;
  };
  readonly className?: string;
}

/**
 * The chat on a phone: a full-screen dialog exactly the size of the visible area, with header, transcript and composer
 * in one column. The package owns the browser problems of that surface: the layer follows `visualViewport` (no gap above
 * the keyboard, no page showing through), the page behind is inert and not scrolled or shifted, Back and Escape close
 * it, and the transcript stays pinned to the newest message while the keyboard opens (`Transcript`).
 */
export function ChatSheet({ open, onOpenChange, title, heading: custom, description, closeLabel = "Close", actions, children, behaviour, className }: ChatSheetProps) {
  const layer = useRef<HTMLDivElement | null>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  const sized = useViewportBox<HTMLDivElement>(open && behaviour?.viewport !== false);
  const attach = useCallback(
    (node: HTMLDivElement | null) => {
      layer.current = node;
      sized(node);
    },
    [sized],
  );
  useLayer(open, useCallback(() => onOpenChange(false), [onOpenChange]), {
    back: behaviour?.back,
    inert: behaviour?.inert,
    appRoot: behaviour?.appRoot,
    lockScroll: behaviour?.lockScroll,
    layer: () => layer.current,
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        ref={attach}
        fullscreen
        closeButton={false}
        className={`chat-sheet ${className ?? ""}`}
        onOpenAutoFocus={(event) => {
          if (behaviour?.autoFocus) return;
          event.preventDefault();
          heading.current?.focus({ preventScroll: true });
        }}
      >
        <ChatPanelHeader
          heading={
            custom ? (
              <>
                <DialogTitle ref={heading} tabIndex={-1} className="sr-only">
                  {title}
                </DialogTitle>
                {custom}
              </>
            ) : (
              <DialogTitle ref={heading} tabIndex={-1} className={PANEL_TITLE_CLASS}>
                {title}
              </DialogTitle>
            )
          }
          description={description ? <DialogDescription className="truncate">{description}</DialogDescription> : undefined}
          actions={actions}
          close={
            <DialogClose asChild>
              <PanelCloseButton label={closeLabel} />
            </DialogClose>
          }
        />
        <div className="chat-sheet-body">{children}</div>
      </DialogContent>
    </Dialog>
  );
}
