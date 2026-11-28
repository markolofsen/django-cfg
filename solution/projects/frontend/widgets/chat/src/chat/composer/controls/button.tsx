import type { ButtonHTMLAttributes, ReactNode, Ref } from "react";
import { TooltipHint, type TooltipProp } from "@djangocfg/ui-core";

/**
 * One control in the composer's toolbar row.
 *
 * Four buttons arrived here with four different answers to "what does a control
 * look like": the engine chip tinted itself with `accent` — BLUE in this theme,
 * so hovering lit up a filled pill beside the blue send button — the
 * dictation-language caret used `accent` too, the mic changed only its text
 * colour and so appeared to have no hit box at all, and send is permanently
 * filled with no hover at all. Read as a row they were four unrelated widgets.
 *
 * A component rather than a `.composer-box button` rule is what makes that
 * stay fixed: three of these are owned by DIFFERENT packages, so a descendant
 * selector would style whatever they happen to render and silently lose to any
 * utility class they carry. Asking for the component is a decision each caller
 * makes once; inheriting from an ancestor is a coincidence of nesting.
 *
 * It renders a `<button>` (plus the hover name when `tooltip` is given: the
 * ui-core `TooltipHint`, silent on touch devices) so a host that needs a menu or a
 * popover wraps this, and every one of them still agrees about size, radius and hover.
 */

export type ComposerButtonTone = "neutral" | "primary";

export interface ComposerButtonProps
  extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "className"> {
  /**
   * `primary` is the SEND action, and there is exactly one of it. A second
   * filled control in the row would make the composer offer two equal answers
   * to "what does Enter do".
   */
  readonly tone?: ComposerButtonTone;
  /**
   * Wider than square, for a control that carries text (the engine chip).
   *
   * The default is the 32px square every icon control uses; text needs room
   * either side of it, and stretching the square by padding alone would make
   * the two kinds disagree about height.
   */
  readonly wide?: boolean;
  /** Hover name; mirror the `aria-label`. Absent on touch devices by itself. */
  readonly tooltip?: TooltipProp;
  readonly className?: string;
  readonly children?: ReactNode;
  readonly ref?: Ref<HTMLButtonElement>;
}

const BASE =
  // The design system's control radius, matching the box around them: both are
  // rounded rectangles from the same scale, so the row reads as one object.
  // (It was `rounded-full` while the box was a capsule — the box drives this.)
  "shrink-0 items-center justify-center rounded-[var(--chat-composer-button-radius,var(--radius-control,0.625rem))] transition-colors " +
  // Height DERIVED from the field beside it, never a literal — a hardcoded 32px
  // silently went 2px short the moment the body text moved from 15px to 16. The
  // expression lives in `composer.css`, which needs the same number to keep the
  // box's capsule radius concentric with these circles; two copies of one
  // measurement is exactly how the corners stop matching.
  "h-[var(--chat-composer-control-h,2.125rem)] disabled:opacity-40 " +
  // Focus is the host theme's ring, borrowed rather than imported — this
  // package declares no dependency on a component library.
  "outline-none focus-visible:outline-2 focus-visible:outline-offset-2 " +
  "focus-visible:outline-[var(--ring,currentColor)] " +
  "[&_svg]:size-4 [&_svg]:shrink-0";

const TONES: Record<ComposerButtonTone, string> = {
  // A quiet plate on hover, never a tint. `--accent` is the theme's highlight
  // (blue here), and a filled blue plate beside the blue send button reads as a
  // second primary action rather than as a hover.
  neutral:
    "text-muted-foreground not-disabled:hover:bg-muted not-disabled:hover:text-foreground " +
    "aria-expanded:bg-muted aria-expanded:text-foreground",
  // Already filled, so it answers with depth instead of a plate.
  primary: "bg-primary text-primary-foreground not-disabled:hover:brightness-95",
};

export function ComposerButton({
  tone = "neutral",
  wide = false,
  tooltip,
  className,
  children,
  ref,
  type = "button",
  ...rest
}: ComposerButtonProps) {
  // `flex` for the wide variant, `grid` for the square one — and the difference
  // is load-bearing, not cosmetic. A single-column grid stacks its children in
  // ROWS, so a chip carrying icon + label + caret put the caret on a third row
  // and pushed it out through the button's fixed 32px height, below the
  // composer's own edge. Flex lays the same three out along the row, which is
  // what `gap-1.5` was always describing.
  // `aspect-square` rather than a second copy of the height expression: the
  // square variant must stay square whatever that height resolves to, and
  // repeating the calc is how the two drift apart.
  const width = wide ? "flex gap-1.5 px-2.5" : "grid aspect-square";
  const button = (
    <button
      {...rest}
      ref={ref}
      type={type}
      className={`${BASE} ${width} ${TONES[tone]} ${className ?? ""}`}
    >
      {children}
    </button>
  );
  return (
    <TooltipHint tooltip={tooltip} disabled={rest.disabled}>
      {button}
    </TooltipHint>
  );
}
