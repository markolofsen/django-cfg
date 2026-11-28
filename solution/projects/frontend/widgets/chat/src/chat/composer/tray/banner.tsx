/**
 * A notice block ABOVE the composer box: a limit approaching, a plan to review.
 *
 * Above rather than inside, which is what separates it from `ComposerQueue`.
 * The queue describes the DRAFT and belongs within the same rounded surface;
 * this describes the account or the session and would read as part of the
 * message if it shared that surface.
 *
 * Form adapted from vercel/ai-elements `checkpoint.tsx` and `confirmation.tsx`
 * (Apache-2.0, submodule @ 6a9d5b1): composed parts rather than one component
 * with a prop per feature. Their `Alert`-based shell and shadcn `Button` are
 * NOT copied — this package styles against `ui-core` tokens and ships its own
 * button, so only the composition survives the crossing.
 *
 * Composition is the whole point here, not taste. The predecessor exposed
 * `icon`, `title`, `description`, `actions[]`, `variant`, `onDismiss` and
 * `className` — seven props, and a caller wanting a second line or a link had
 * no route but an eighth. Parts leave that to the caller's JSX.
 *
 * Copy is the HOST's: nothing here reads the dictionary, because a banner's
 * words are always about the host's own situation (an allowance, a plan, a
 * quota). `dismissLabel` is the exception and is required — an icon-only
 * control needs an accessible name in all 17 locales, and a hardcoded English
 * one is what this package exists to stop shipping.
 */

import type { ReactNode } from "react";
import { X } from "lucide-react";

/** Tints the ICON only; the surface stays neutral so a notice never shouts. */
export type ComposerBannerTone = "info" | "warning" | "upgrade";

const ICON_TINT: Record<ComposerBannerTone, string> = {
  info: "text-muted-foreground",
  warning: "text-destructive",
  upgrade: "text-primary",
};

export interface ComposerBannerProps {
  readonly children: ReactNode;
  readonly className?: string;
}

/** The surface. Lay out its parts in the order they should read. */
export function ComposerBanner({ children, className }: ComposerBannerProps) {
  return (
    <div
      // `role="status"`, not `alert`: every use is ambient. An alert interrupts,
      // and a limit approaching is not worth taking focus for.
      role="status"
      data-slot="composer-banner"
      className={`flex w-full items-start gap-3 rounded-2xl border border-border bg-muted/60 px-3.5 py-3 text-sm text-foreground ${className ?? ""}`}
    >
      {children}
    </div>
  );
}

export interface ComposerBannerIconProps {
  readonly children: ReactNode;
  readonly tone?: ComposerBannerTone;
}

export function ComposerBannerIcon({
  children,
  tone = "info",
}: ComposerBannerIconProps) {
  return (
    <span
      className={`mt-0.5 flex shrink-0 [&_svg]:size-5 ${ICON_TINT[tone]}`}
      aria-hidden
    >
      {children}
    </span>
  );
}

/** Title and body. `min-w-0` so a long word truncates instead of pushing the
 *  actions off the row. */
export function ComposerBannerBody({ children, className }: ComposerBannerProps) {
  return (
    <div className={`min-w-0 flex-1 ${className ?? ""}`}>{children}</div>
  );
}

export function ComposerBannerTitle({ children }: { readonly children: ReactNode }) {
  return <p className="font-semibold leading-snug">{children}</p>;
}

export function ComposerBannerDescription({
  children,
}: {
  readonly children: ReactNode;
}) {
  return <p className="mt-0.5 text-xs text-muted-foreground">{children}</p>;
}

/** Holds the buttons. Two is the practical limit — a notice offering three
 *  routes is a dialog wearing a banner's clothes. */
export function ComposerBannerActions({ children }: { readonly children: ReactNode }) {
  return <div className="flex shrink-0 items-center gap-1.5">{children}</div>;
}

export interface ComposerBannerActionProps {
  readonly children: ReactNode;
  readonly onClick: () => void;
  /** `primary` fills; `outline` (default) stays bordered and neutral. */
  readonly variant?: "primary" | "outline";
}

const ACTION_CLASS: Record<
  NonNullable<ComposerBannerActionProps["variant"]>,
  string
> = {
  primary: "bg-primary text-primary-foreground hover:bg-primary/90",
  outline:
    "border border-border bg-background text-foreground hover:bg-accent hover:text-accent-foreground",
};

export function ComposerBannerAction({
  children,
  onClick,
  variant = "outline",
}: ComposerBannerActionProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex h-8 cursor-pointer items-center justify-center rounded-lg px-3 text-xs font-medium transition-colors focus-visible:ring-1 focus-visible:ring-ring focus-visible:outline-none ${ACTION_CLASS[variant]}`}
    >
      {children}
    </button>
  );
}

export interface ComposerBannerDismissProps {
  readonly onDismiss: () => void;
  /** Required: an icon-only control with no name is invisible to a reader. */
  readonly label: string;
}

export function ComposerBannerDismiss({
  onDismiss,
  label,
}: ComposerBannerDismissProps) {
  return (
    <button
      type="button"
      onClick={onDismiss}
      aria-label={label}
      title={label}
      className="-mt-1 -mr-1 inline-flex size-7 shrink-0 cursor-pointer items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:ring-1 focus-visible:ring-ring focus-visible:outline-none"
    >
      <X className="size-4" aria-hidden />
    </button>
  );
}
