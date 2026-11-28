'use client';

/**
 * SidePanel — a non-modal side drawer.
 *
 * Use for inspector panels, playgrounds, filters — anywhere you want a
 * slide-in surface that does NOT lock out the rest of the page. The
 * surrounding UI stays clickable, focusable and scrollable.
 *
 * Esc, the close button and a click outside all dismiss it. Having no backdrop
 * says the page stays usable; it does not say the click should do nothing —
 * a reader who clicks beside the panel expects it to close, and with only Esc
 * and a small `×` they had to hunt for the way out.
 *
 * Differences from the existing ``Drawer``:
 *   - ``modal={false}``  — no focus trap, no scroll-lock on <body>.
 *   - No backdrop overlay (the page behind stays legible and live).
 *   - No ``shouldScaleBackground`` (vaul's iOS-style fancy scale looks
 *     wrong for side panels — reserved for bottom sheets).
 *   - Opinionated for ``right``/``left`` directions; vaul still drives
 *     the transform + swipe-to-close gesture underneath.
 *
 * Layout is intentionally similar to our Sheet/Drawer components so
 * callers feel at home.
 */

import * as React from 'react';
import { Drawer as DrawerPrimitive } from 'vaul';
import { X } from 'lucide-react';

import { useComposedRefs } from '../../../lib/compose-refs';
import { cn } from '../../../lib/utils';

// ─── Root ─────────────────────────────────────────────────────────────────────

// A menu, popover or listbox opened from inside the panel is portalled to <body>, so it is "outside" the panel in the DOM. While one is
// open, a press or Esc belongs to that layer (it closes itself); the panel must not also go. Without this, closing a "..." menu by
// clicking away or pressing Esc took the whole panel with it. A closing layer keeps `data-state="closed"` for its exit animation.
const NESTED_LAYER =
    '[data-slot="popover-content"],[role="menu"],[role="listbox"],[data-radix-popper-content-wrapper]';
function nestedLayerOpen(): boolean {
    return Array.from(document.querySelectorAll(NESTED_LAYER)).some(
        (el) => el.getAttribute('data-state') !== 'closed' && !el.closest('[data-state="closed"]'),
    );
}

export interface SidePanelProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    children: React.ReactNode;
    /** ``'right'`` (default) slides in from the right edge; ``'left'`` from the left. */
    side?: 'right' | 'left';
    /** Close when the user presses Escape. Default ``true``. Disable when
     *  the parent wants custom handling or Esc is bound to something else. */
    closeOnEsc?: boolean;
    /**
     * Close when the user clicks or taps outside the panel. Default ``true``.
     *
     * Having no backdrop is a statement about the PAGE — it stays readable and
     * clickable — not about the click. Without this the only ways out were Esc
     * and a small ``×``, so a reader who clicked beside the panel, as every
     * other overlay has taught them to, got nothing and had to go hunting for
     * the button.
     *
     * Turn it off for a panel the reader works ALONGSIDE — an inspector kept
     * open while editing the page behind it, where a stray click on the canvas
     * must not dismiss the thing they are reading from.
     */
    closeOnOutsideClick?: boolean;
    /**
     * Dim the page behind the panel. Default ``false`` (the page stays legible and live).
     *
     * For a panel that covers content the reader is not meant to work in while it is open (a chat that
     * slides over the page because the window has no room for a column): the dimming says the page is
     * behind it. It is a plain layer, not a modal: no focus trap, no scroll lock; a press on it closes
     * the panel through ``closeOnOutsideClick``.
     */
    backdrop?: boolean;
}

const SidePanel: React.FC<SidePanelProps> & {
    Content: typeof SidePanelContent;
    Header: typeof SidePanelHeader;
    Title: typeof SidePanelTitle;
    Description: typeof SidePanelDescription;
    Body: typeof SidePanelBody;
    Footer: typeof SidePanelFooter;
    Close: typeof SidePanelClose;
} = ({ open, onOpenChange, children, side = 'right', closeOnEsc = true, closeOnOutsideClick = true, backdrop = false }) => {
    // The panel element, so the outside-click listener can ask "was this click
    // inside?" — there is no backdrop to catch it for us.
    const contentRef = React.useRef<HTMLDivElement | null>(null);

    // Esc handling: vaul's built-in closes on Esc only when modal=true.
    // We're non-modal, so we install our own listener — gated on ``open``
    // to avoid swallowing Esc globally while the panel is closed.
    React.useEffect(() => {
        if (!open || !closeOnEsc) return;
        const handler = (e: KeyboardEvent) => {
            // Radix layers handle Esc first (capture phase) and mark it handled.
            if (e.key === 'Escape' && !e.defaultPrevented && !nestedLayerOpen()) onOpenChange(false);
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [open, closeOnEsc, onOpenChange]);

    // Outside-click handling, for the same reason Esc is handled here: with
    // `modal={false}` vaul installs no dismissal of its own.
    //
    // `pointerdown` rather than `click`, so a press that begins outside closes
    // even if the pointer travels onto the panel before release. The listener
    // is added on a later task, otherwise the very click that OPENED the panel
    // finishes propagating into it and closes it again immediately.
    React.useEffect(() => {
        if (!open || !closeOnOutsideClick) return;

        let armed = false;
        const arm = () => { armed = true; };
        const id = window.setTimeout(arm, 0);

        const handler = (event: PointerEvent) => {
            if (!armed) return;
            if (nestedLayerOpen()) return;
            const target = event.target as Node | null;
            if (!target || contentRef.current?.contains(target)) return;
            // A click inside any overlay the panel itself opened — a Select's
            // popover, a dialog — lands outside the panel in the DOM, because
            // both are portalled to <body>. Closing on those would dismiss the
            // panel the moment a reader picked a value in it.
            if (
                target instanceof Element &&
                target.closest('[data-slot="popover-content"],[role="dialog"],[role="listbox"],[role="menu"]')
            ) {
                return;
            }
            onOpenChange(false);
        };

        document.addEventListener('pointerdown', handler, true);
        return () => {
            window.clearTimeout(id);
            document.removeEventListener('pointerdown', handler, true);
        };
    }, [open, closeOnOutsideClick, onOpenChange]);

    const contextValue = React.useMemo(() => ({ side, contentRef, backdrop }), [side, backdrop]);

    return (
        <DrawerPrimitive.Root
            open={open}
            onOpenChange={onOpenChange}
            direction={side}
            modal={false}
            shouldScaleBackground={false}
            // vaul defaults to mutating ``<body>`` styles (position:fixed,
            // overflow:hidden, pointer-events:none) to support swipe-to-
            // close. For a non-modal side panel that behaviour is wrong —
            // it disables every interaction outside the panel including
            // page scroll. ``noBodyStyles`` tells vaul to keep its hands
            // off the document.
            noBodyStyles
            disablePreventScroll
            dismissible
        >
            <SidePanelSideContext.Provider value={contextValue}>
                {children}
            </SidePanelSideContext.Provider>
        </DrawerPrimitive.Root>
    );
};
SidePanel.displayName = 'SidePanel';

// Carries the side down to Content so it can place border + transform correctly.
const SidePanelSideContext = React.createContext<{
    side: 'right' | 'left';
    contentRef?: React.MutableRefObject<HTMLDivElement | null>;
    backdrop?: boolean;
}>({ side: 'right' });

// ─── Content ──────────────────────────────────────────────────────────────────

export interface SidePanelContentProps extends React.ComponentPropsWithoutRef<typeof DrawerPrimitive.Content> {
    /** CSS width (any valid value: ``'440px'``, ``'32rem'``, ``'min(440px, 90vw)'``).
     *  Default ``'440px'``. Override via ``className`` with ``w-*`` if you
     *  prefer Tailwind. */
    width?: string;
}

const SidePanelContent = React.forwardRef<
    React.ElementRef<typeof DrawerPrimitive.Content>,
    SidePanelContentProps
>(({ className, children, width = '440px', style, ...props }, ref) => {
    const { side, contentRef, backdrop } = React.useContext(SidePanelSideContext);
    // Both refs always compose: the caller's, and the panel's own, which the
    // outside-click listener measures against.
    const composedRef = useComposedRefs(ref, contentRef ?? null);
    const positioning =
        side === 'right' ? 'inset-y-0 right-0 border-l' : 'inset-y-0 left-0 border-r';

    return (
        <DrawerPrimitive.Portal>
            {backdrop ? <div aria-hidden="true" data-slot="side-panel-backdrop" className="fixed inset-0 z-499 bg-overlay animate-in fade-in-0" /> : null}
            <DrawerPrimitive.Content
                ref={composedRef}
                aria-describedby={undefined}
                className={cn(
                    'fixed z-500 flex flex-col bg-background shadow-2xl shadow-black/20',
                    'h-full max-w-[95vw]',
                    positioning,
                    className,
                )}
                style={{
                    width,
                    // Animate both the slide-in (transform, driven by vaul)
                    // and width changes (when callers swap width to reveal
                    // secondary content). Separate transition strings so
                    // the two can have different curves if needed.
                    transition:
                        'transform 300ms cubic-bezier(0.32, 0.72, 0, 1),' +
                        ' width 250ms cubic-bezier(0.32, 0.72, 0, 1)',
                    ...style,
                }}
                {...props}
            >
                {children}
            </DrawerPrimitive.Content>
        </DrawerPrimitive.Portal>
    );
});
SidePanelContent.displayName = 'SidePanelContent';

// ─── Header / Title / Description ─────────────────────────────────────────────

const SidePanelHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
    ({ className, ...props }, ref) => (
        <div
            ref={ref}
            className={cn(
                'shrink-0 flex items-center gap-3 px-4 h-12 border-b bg-muted/20',
                className,
            )}
            {...props}
        />
    ),
);
SidePanelHeader.displayName = 'SidePanelHeader';

const SidePanelTitle = React.forwardRef<
    React.ElementRef<typeof DrawerPrimitive.Title>,
    React.ComponentPropsWithoutRef<typeof DrawerPrimitive.Title>
>(({ className, ...props }, ref) => (
    <DrawerPrimitive.Title
        ref={ref}
        className={cn(
            'text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground/60',
            className,
        )}
        {...props}
    />
));
SidePanelTitle.displayName = 'SidePanelTitle';

const SidePanelDescription = React.forwardRef<
    React.ElementRef<typeof DrawerPrimitive.Description>,
    React.ComponentPropsWithoutRef<typeof DrawerPrimitive.Description>
>(({ className, ...props }, ref) => (
    <DrawerPrimitive.Description
        ref={ref}
        className={cn('text-xs text-muted-foreground', className)}
        {...props}
    />
));
SidePanelDescription.displayName = 'SidePanelDescription';

// ─── Body / Footer ────────────────────────────────────────────────────────────

const SidePanelBody = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
    ({ className, ...props }, ref) => (
        <div
            ref={ref}
            className={cn('flex-1 min-h-0 overflow-y-auto', className)}
            {...props}
        />
    ),
);
SidePanelBody.displayName = 'SidePanelBody';

const SidePanelFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
    ({ className, ...props }, ref) => (
        <div
            ref={ref}
            className={cn('shrink-0 border-t px-4 py-3 bg-background/95', className)}
            {...props}
        />
    ),
);
SidePanelFooter.displayName = 'SidePanelFooter';

// ─── Close ────────────────────────────────────────────────────────────────────

export interface SidePanelCloseProps
    extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'type' | 'children'> {
    /** Accessible label. Default ``"Close panel"``. */
    label?: string;
    /** Replace the default ``X`` icon with custom content. */
    children?: React.ReactNode;
}

const SidePanelClose = React.forwardRef<HTMLButtonElement, SidePanelCloseProps>(
    ({ className, label = 'Close panel', children, ...props }, ref) => (
        <DrawerPrimitive.Close asChild>
            <button
                ref={ref}
                type="button"
                aria-label={label}
                title={`${label} (Esc)`}
                className={cn(
                    'shrink-0 h-7 w-7 inline-flex items-center justify-center rounded-[var(--radius-sm)]',
                    'text-muted-foreground hover:text-foreground hover:bg-muted transition-colors',
                    className,
                )}
                {...props}
            >
                {children ?? <X className="h-4 w-4" />}
            </button>
        </DrawerPrimitive.Close>
    ),
);
SidePanelClose.displayName = 'SidePanelClose';

// Attach subcomponents to the root for ergonomic dot-access.
SidePanel.Content = SidePanelContent;
SidePanel.Header = SidePanelHeader;
SidePanel.Title = SidePanelTitle;
SidePanel.Description = SidePanelDescription;
SidePanel.Body = SidePanelBody;
SidePanel.Footer = SidePanelFooter;
SidePanel.Close = SidePanelClose;

export {
    SidePanel,
    SidePanelContent,
    SidePanelHeader,
    SidePanelTitle,
    SidePanelDescription,
    SidePanelBody,
    SidePanelFooter,
    SidePanelClose,
};
