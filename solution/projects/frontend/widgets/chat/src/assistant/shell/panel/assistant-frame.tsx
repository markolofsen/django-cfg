'use client';

import { useCallback, useEffect, useRef, useState, type CSSProperties, type KeyboardEvent, type PointerEvent, type ReactNode } from 'react';

import { useHotkey } from '@djangocfg/ui-core/hooks';
import { ChatPanelHeader, PanelCloseButton } from '../../../chat/ui';

import { ASSISTANT_TOGGLE } from '../composer/keys';
import { AssistantSlot, useHeaderActions } from './host';
import { useAssistantCopy } from '../../../i18n/assistant';
import { GatedBody, type AssistantLockOptions } from '../access/assistant-auth-gate';
import { ChatDock } from './chat-dock';
import { headerActions, headingNode } from './header-slots';
import { columnLimit, useMediaQuery, useViewportWidth } from './panel-state';

export interface FrameLabels {
  /** Name of the column and its heading (the host's brand). */
  title: string;
  /** Absent: the bundled words for the active language. */
  close?: string;
  /** Name of the width handle. */
  resize?: string;
}

interface Props {
  /** The assistant is open. The frame decides where it lives by the window's width (`dockFrom`): a column, a floating window or a sheet. */
  docked: boolean;
  /**
   * The narrowest window (px) that still has room for a column beside the page. Default 1280 (`DOCK_FROM`, also the default `restoreFrom` of `createAssistantUi`), so a host passes nothing.
   * Below it the same chat opens as a floating window over the page, bottom right (tablet, not modal), or a full-screen sheet (phone) instead of squeezing the content: `ChatDock`, wired here
   * with the frame's own title, close and actions, so a host renders no dock of its own. `0`: never self-dock, always a column (the host then draws its own dock below its own width).
   */
  dockFrom?: number;
  /** Show the signed-out view (big icon, reason, "Sign in") instead of the chat to a reader who is not signed in, from the django-cfg auth state. Same in the column and in the dock. */
  requireAuth?: boolean;
  /** Words, icon, destination or a whole block for the signed-out view. */
  lock?: AssistantLockOptions;
  width: number;
  minWidth: number;
  maxWidth: number;
  defaultWidth: number;
  onWidthChange: (width: number) => void;
  onClose: () => void;
  /**
   * Makes the open state settable from the keyboard: with it the frame binds `hotkey` (default ⌘J / Ctrl+J) to "toggle", from anywhere on the page and from inside
   * a text field. The host passes its own setter (`setOpen`). Absent: no key is bound.
   */
  onOpenChange?: (open: boolean) => void;
  /** The combination for `onOpenChange` (a `useHotkey` string). `false` turns the key off. The floating button's tooltip shows the same default. */
  hotkey?: string | false;
  labels: FrameLabels;
  /** Header controls beside the close button (for example `SessionsMenu`): one header, a thin divider keeps them apart from Close. */
  actions?: ReactNode;
  /** What the column shows instead of the chat (the locked view, a notice). Absent: the chat itself. */
  content?: ReactNode;
  /** Replaces the title in the header (a Chat | People segment, a count beside the title). Absent: the `labels.title` heading. The column's `aria-label` stays the title. */
  heading?: ReactNode;
  /** The round Help `?` before the actions. Absent: `AssistantHelp`. `false`: none. A node: the host's own (`<AssistantHelp rows={...} />`). */
  help?: ReactNode | false;
  /**
   * Below `dockFrom` and from 768 px up: `window` (default) is the floating window bottom right, `sheet` the full-screen sheet of a phone. A phone (under 768 px) always gets the sheet.
   * A call picks `window` with `windowBottom` so the window never covers its control bar.
   */
  tablet?: 'window' | 'sheet';
  /** The floating window's distance from the bottom edge (a CSS length, default `1rem`); its height shrinks to fit above it. */
  windowBottom?: string;
  /** On a phone the sheet closes when the page moves to another path (a query or hash change keeps it). Default true; `false` keeps it open across pages. */
  closeOnNavigate?: boolean;
  /**
   * The narrowest the page may be left by the column (px). The column's largest width is then `min(maxWidth, viewport - stageMin)`, never below `minWidth`: a call keeps its stage at 480 px or more.
   * The remembered width is not rewritten; it only applies as far as the room allows.
   */
  stageMin?: number;
  /** Classes of the frame's root. */
  className?: string;
  /**
   * The frame fills a box the host sized (for example `className="fixed inset-0 h-dvh"` around a full-screen page), instead of being the document's flow with a `sticky h-dvh` column:
   * the column is as tall as the box, and the page is a flex column that takes the rest of the width.
   */
  fill?: boolean;
  /** The page. */
  children: ReactNode;
}

/** The window width from which the assistant is a column beside the page, below it a floating window or a sheet. */
export const DOCK_FROM = 1280;

/** How long the column takes to open or close; the same number is in `layout.css`. */
const MOTION_MS = 380;
/** A column restored at page load is already there: only a change after this long is animated. */
const RESTORE_GRACE_MS = 800;

/**
 * The page with the assistant column beside it. While `docked`, the page narrows and the column stands at the right edge, full height. Its width is published as the CSS
 * variable `--assistant-w` (`0px` when closed) so fixed elements of the host keep clear of it. Page scroll stays the window's: the column is `sticky`, not a scroll container.
 *
 * Opening and closing move that variable, not the column: the page eases to its new width and the column is revealed from the right edge at its full width (nothing inside
 * reflows), with a short fade. `--assistant-w` is a registered length (`layout.css`), so fixed host elements follow the same curve. The column stays mounted until the
 * close finishes. Resizing by hand and the first paint after a page load are not animated.
 */
export function AssistantFrame({ docked: wanted, dockFrom = DOCK_FROM, requireAuth, lock, width, minWidth, maxWidth, defaultWidth, onWidthChange, onClose, onOpenChange, hotkey = ASSISTANT_TOGGLE, labels, content, actions, heading, help, tablet, windowBottom, closeOnNavigate, stageMin, className, fill, children }: Props) {
  useHotkey(hotkey || ASSISTANT_TOGGLE, () => onOpenChange?.(!wanted), {
    enabled: Boolean(hotkey) && onOpenChange !== undefined,
    inInput: true,
    preventDefault: true,
    description: 'Open or close the assistant',
  });
  const wide = useMediaQuery(`(min-width: ${dockFrom}px)`);
  // `wanted` means open: the column needs the room, the dock does not.
  const docked = wanted && wide;
  // The dock stays mounted while the window is narrow and is driven by `open`: unmounting it on close would cut the exit animation.
  const overlay = !wide;
  const published = useHeaderActions();
  const born = useRef(0);
  const [mounted, setMounted] = useState(false);
  const [shown, setShown] = useState(false);
  const [moving, setMoving] = useState(false);

  useEffect(() => {
    if (!born.current) born.current = performance.now();
    const timers: number[] = [];
    let frame = 0;
    if (docked) {
      setMounted(true);
      if (performance.now() - born.current < RESTORE_GRACE_MS) {
        setMoving(false);
        setShown(true);
      } else {
        // Mount at zero width, then (two frames on, so the browser has laid out the start) move to the real one.
        setMoving(true);
        frame = requestAnimationFrame(() => {
          frame = requestAnimationFrame(() => setShown(true));
        });
        timers.push(window.setTimeout(() => setMoving(false), MOTION_MS + 40));
      }
    } else {
      setMoving(true);
      setShown(false);
      timers.push(
        window.setTimeout(() => {
          setMounted(false);
          setMoving(false);
        }, MOTION_MS + 40),
      );
    }
    return () => {
      cancelAnimationFrame(frame);
      timers.forEach(window.clearTimeout);
    };
  }, [docked]);

  // The widest the column may be here: the host's cap, or less when the page must keep `stageMin`.
  const viewport = useViewportWidth();
  const limit = columnLimit({ minWidth, maxWidth, viewport, stageMin });
  const shownWidth = Math.min(width, limit);
  const style = { '--assistant-w': shown ? `${shownWidth}px` : '0px' } as CSSProperties;
  return (
    <div className={`assistant-frame flex${className ? ` ${className}` : ''}`} data-moving={moving ? 'true' : 'false'} style={style}>
      <div className={fill ? 'relative flex min-h-0 min-w-0 flex-1 flex-col' : 'min-w-0 flex-1'}>{children}</div>
      {overlay ? (
        <ChatDock open={wanted} onOpenChange={(open) => !open && onClose()} title={labels.title} closeLabel={labels.close} actions={actions ?? published} heading={heading} help={help} tablet={tablet} windowBottom={windowBottom} closeOnNavigate={closeOnNavigate}>
          <GatedBody requireAuth={requireAuth} lock={lock}>{content ?? <AssistantSlot className="h-full min-h-0" />}</GatedBody>
        </ChatDock>
      ) : null}
      {mounted ? <Column {...{ width: shownWidth, shown, minWidth, maxWidth: limit, defaultWidth, onWidthChange, onClose, labels, content, actions, heading, help, requireAuth, lock, fill }} /> : null}
    </div>
  );
}

function Column({ width, shown, minWidth, maxWidth, defaultWidth, onWidthChange, onClose, labels, content, actions, heading, help, requireAuth, lock, fill }: Omit<Props, 'docked' | 'children'> & { shown: boolean }) {
  const copy = useAssistantCopy();
  const published = useHeaderActions();
  // The handle sits on the column's left edge: the pointer's distance from the window's right edge is the new width.
  const drag = useCallback(
    (event: PointerEvent<HTMLDivElement>) => {
      event.preventDefault();
      const handle = event.currentTarget;
      handle.setPointerCapture(event.pointerId);
      const move = (e: globalThis.PointerEvent) => onWidthChange(Math.min(maxWidth, window.innerWidth - e.clientX));
      const stop = () => {
        handle.removeEventListener('pointermove', move);
        handle.removeEventListener('pointerup', stop);
        handle.removeEventListener('pointercancel', stop);
      };
      handle.addEventListener('pointermove', move);
      handle.addEventListener('pointerup', stop);
      handle.addEventListener('pointercancel', stop);
    },
    [onWidthChange, maxWidth],
  );
  const key = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'ArrowLeft') onWidthChange(Math.min(maxWidth, width + 24));
    else if (event.key === 'ArrowRight') onWidthChange(width - 24);
    else if (event.key === 'Home') onWidthChange(defaultWidth);
    else return;
    event.preventDefault();
  };

  return (
    // The clip: as wide as the page has given so far, and it owns the divider, so the hairline is there from the first frame and travels with the leading edge (a border on the column would be clipped away until the very end). the column inside keeps its full width and is anchored right, so it slides in instead of squeezing.
    <div className={`assistant-clip box-border flex shrink-0 justify-end overflow-hidden border-l ${fill ? 'h-full self-stretch' : 'sticky top-0 h-dvh self-start'}`} data-shown={shown ? 'true' : 'false'}>
    <aside aria-label={labels.title} style={{ width }} className="assistant-column relative flex h-full shrink-0 flex-col bg-background">
      <div
        role="separator"
        aria-orientation="vertical"
        aria-label={labels.resize ?? copy.resize}
        aria-valuemin={minWidth}
        aria-valuemax={maxWidth}
        aria-valuenow={width}
        tabIndex={0}
        onPointerDown={drag}
        onKeyDown={key}
        onDoubleClick={() => onWidthChange(defaultWidth)}
        className="absolute inset-y-0 -left-1 z-10 w-2 cursor-col-resize touch-none outline-none transition-colors hover:bg-primary/30 focus-visible:bg-primary/40"
      />
      <ChatPanelHeader
        heading={headingNode(heading, labels.title)}
        actions={headerActions(help, actions ?? published)}
        close={<PanelCloseButton label={labels.close ?? copy.close} onClick={onClose} />}
      />
      <GatedBody requireAuth={requireAuth} lock={lock}>
        {content ? <div className="flex min-h-0 flex-1 flex-col">{content}</div> : <AssistantSlot className="min-h-0 flex-1" />}
      </GatedBody>
    </aside>
    </div>
  );
}
