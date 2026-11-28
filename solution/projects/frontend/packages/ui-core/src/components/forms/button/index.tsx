"use client"

import { cva, type VariantProps } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import * as React from 'react';

import { Slot } from '@radix-ui/react-slot';

import { cn } from '../../../lib/utils';
import { Link } from '../../navigation/link';
import { TooltipHint, type TooltipProp } from '../../overlay/tooltip';
import { buttonSizeClass, CONTROL_SIZE } from '../control-size';

const buttonVariants = cva(
  "inline-flex cursor-pointer items-center justify-center gap-2 whitespace-nowrap rounded-[var(--radius)] text-sm font-(weight:--button-weight) transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        // `border-border`, never `border-input`: `--input` is the FILL token
        // for a field's surface, and in the light theme it is the page colour
        // itself (97% L) — an outline button drawn with it had no visible edge
        // at all. `--border` (86% L) is the token for an edge. Same pairing
        // `Input` and `InputGroup` use.
        outline:
          "border border-border bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      // Height comes from the shared control ladder, so a Button at any size
      // lines up with the Input / Select trigger of the same size. Only the
      // corner radius is decided here.
      size: {
        default: buttonSizeClass('default'),
        sm: cn(buttonSizeClass('sm'), "rounded-[var(--radius)]"),
        xs: cn(buttonSizeClass('xs'), "rounded-[var(--radius-sm)]"),
        lg: cn(buttonSizeClass('lg'), "rounded-[var(--radius)]"),
        huge: cn(buttonSizeClass('huge'), "rounded-[var(--radius)]"),
        icon: cn(CONTROL_SIZE.default.height, "w-(--control-h-default) pointer-coarse:min-w-11"),
      },
      // Most variants ship a baked-in `shadow`/`shadow-sm` for a lifted look.
      // `elevated={false}` flattens that (e.g. controls grouped inside a card —
      // a table's pagination — where a per-button shadow fights the panel).
      // `shadow-none` wins over the variant's shadow: both set `--tw-shadow`
      // and this class is appended after the variant in the utility order.
      elevated: {
        true: "",
        false: "shadow-none",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      elevated: true,
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
  /**
   * The control's hover hint: a text, or `{ content, hotkey?, side?, delay?, hoverable? }` (`TooltipConfig`). Replaces the `Tooltip` / `TooltipTrigger` / `TooltipContent` wrapper.
   * Drawn only where the device can hover (`useCanHover`), so a phone gets none; a disabled button is wrapped in a span so it can still be hovered.
   */
  tooltip?: TooltipProp
}

// Filter out SVG icons from children when loading
function filterIcons(children: React.ReactNode): React.ReactNode {
  return React.Children.map(children, (child) => {
    if (!React.isValidElement(child)) return child;

    const type = child.type;
    // Skip native svg or ForwardRef components (Lucide icons)
    if (type === 'svg' || (typeof type === 'object' && type !== null)) {
      return null;
    }

    return child;
  });
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, elevated, asChild = false, loading = false, onClick, children, disabled, tooltip, ...props }, ref) => {
    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!loading) {
        onClick?.(e);
      }
    };

    // When asChild is true, Slot expects exactly ONE child element
    // Don't render loading spinner with asChild to avoid "Children.only" error
    if (asChild) {
      return (
        <TooltipHint tooltip={tooltip}>
        <Slot
          className={cn(buttonVariants({ variant, size, elevated, className }))}
          ref={ref}
          onClick={onClick}
          {...props}
        >
          {children}
        </Slot>
        </TooltipHint>
      )
    }

    return (
      <TooltipHint tooltip={tooltip} disabled={disabled || loading}>
      <button
        className={cn(buttonVariants({ variant, size, elevated, className }))}
        ref={ref}
        onClick={handleClick}
        disabled={disabled || loading}
        {...props}
      >
        {loading && <Loader2 className="size-4 animate-spin" />}
        {loading ? filterIcons(children) : children}
      </button>
      </TooltipHint>
    )
  }
)
Button.displayName = "Button"

/**
 * ButtonLink — anchor styled as a Button.
 *
 * Renders the framework-agnostic `<Link>` underneath, so SPA navigation,
 * cmd-click, and the Next.js adapter (if mounted) all work out of the box.
 * Drop-in replacement for the previous native-`<a>` version.
 */
/**
 * ButtonLink — anchor styled as a Button.
 *
 * **Disabled / loading.** An `<a>` has no native `disabled`, so we emulate it
 * the shadcn-recommended way: `aria-disabled` + `tabIndex={-1}` +
 * `pointer-events-none opacity-50`, and we cancel the click. `loading` adds the
 * same inert state plus a spinner — keeping parity with `<Button>`.
 */
export interface ButtonLinkProps
  extends Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, 'href'>,
    VariantProps<typeof buttonVariants> {
  href: string
  /** Use replaceState instead of pushState. Default: false. */
  replace?: boolean
  /** Scroll to top after SPA navigation. Default: false. */
  scroll?: boolean
  /** Hint for the host framework's prefetcher (Next.js). */
  prefetch?: boolean | null
  /** Inert + dimmed; click is cancelled and it's removed from tab order. */
  disabled?: boolean
  /** Inert + dimmed + spinner (e.g. while an action resolves). */
  loading?: boolean
  /** The hover hint (see `ButtonProps.tooltip`). */
  tooltip?: TooltipProp
}

const ButtonLink = React.forwardRef<HTMLAnchorElement, ButtonLinkProps>(
  (
    { className, variant, size, elevated, href, replace, scroll, prefetch, disabled = false, loading = false, onClick, children, tooltip, ...props },
    ref,
  ) => {
    // `<a>` can't be natively disabled — emulate it (aria + tab-order + no
    // pointer events) and hard-cancel the click so navigation can't fire.
    const inert = disabled || loading
    const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
      if (inert) {
        e.preventDefault()
        return
      }
      onClick?.(e)
    }

    return (
      <TooltipHint tooltip={tooltip}>
      <Link
        href={href}
        replace={replace}
        scroll={scroll}
        prefetch={prefetch}
        className={cn(
          buttonVariants({ variant, size, elevated, className }),
          inert && 'pointer-events-none opacity-50',
        )}
        ref={ref}
        onClick={handleClick}
        aria-disabled={inert || undefined}
        tabIndex={inert ? -1 : undefined}
        {...props}
      >
        {loading && <Loader2 className="size-4 animate-spin" />}
        {loading ? filterIcons(children) : children}
      </Link>
      </TooltipHint>
    )
  }
)
ButtonLink.displayName = "ButtonLink"

export { Button, ButtonLink, buttonVariants }
