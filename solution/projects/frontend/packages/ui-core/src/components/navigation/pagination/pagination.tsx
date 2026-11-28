"use client";

import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react';
import * as React from 'react';

import { useAppT } from '@djangocfg/i18n';

import { cn } from '../../../lib';
import { type ButtonProps, buttonVariants } from '../../forms/button';
import { Link } from '../link';

const Pagination = ({ className, ...props }: React.ComponentProps<"nav">) => (
  <nav
    role="navigation"
    aria-label="pagination"
    className={cn("mx-auto flex w-full justify-center", className)}
    {...props}
  />
)
Pagination.displayName = "Pagination"

const PaginationContent = React.forwardRef<
  HTMLUListElement,
  React.ComponentProps<"ul">
>(({ className, ...props }, ref) => (
  <ul
    ref={ref}
    className={cn("flex flex-row items-center gap-1", className)}
    {...props}
  />
))
PaginationContent.displayName = "PaginationContent"

const PaginationItem = React.forwardRef<
  HTMLLIElement,
  React.ComponentProps<"li"> & { key?: React.Key }
>(({ className, ...props }, ref) => (
  <li ref={ref} className={cn("", className)} {...props} />
))
PaginationItem.displayName = "PaginationItem"

type PaginationLinkProps = {
  isActive?: boolean
  href?: string
  /**
   * Scroll to the top after navigating. Forwarded to `<Link>`, which defaults
   * it to `false` — so a paginator that omits it leaves the visitor at the
   * scroll offset they had on the previous page, looking at row 40 of a list
   * that now starts again at row 1.
   */
  scroll?: boolean
} & Pick<ButtonProps, "size"> &
  React.ComponentProps<"a">

const PaginationLink = ({
  className,
  isActive,
  size = "icon",
  href,
  scroll,
  children,
  ...props
}: PaginationLinkProps) => {
  const classes = cn(
    buttonVariants({
      variant: isActive ? "outline" : "ghost",
      size,
    }),
    className
  )

  if (href) {
    return (
      <Link
        href={href}
        aria-current={isActive ? "page" : undefined}
        className={classes}
        scroll={scroll}
      >
        {children}
      </Link>
    )
  }

  return (
    <a
      aria-current={isActive ? "page" : undefined}
      className={classes}
      {...props}
    >
      {children}
    </a>
  )
}
PaginationLink.displayName = "PaginationLink"

/* `ui.pagination.*` has shipped translated in all seventeen locales since
   this package gained an i18n layer; only these components never read it, so
   every app using them paginated in English. `useAppT` falls back to the
   English defaults when no provider is mounted, which is what makes this safe
   in a 404 or any tree rendered outside the app shell. */
const PaginationPrevious = ({
  className,
  ...props
}: React.ComponentProps<typeof PaginationLink>) => {
  const t = useAppT();
  return (
    <PaginationLink
      aria-label={t('ui.pagination.previous')}
      size="default"
      className={cn("gap-1", className)}
      {...props}
    >
      {/* ICON ONLY — a chevron pointing back is the settled convention for
          "previous page"; a word beside it adds nothing a reader needs while
          adding a string every locale must carry and every layout must fit.
          The `aria-label` above keeps the name, because a button without one
          is announced as "button". */}
      <ChevronLeft className="h-4 w-4" />
    </PaginationLink>
  )
}
PaginationPrevious.displayName = "PaginationPrevious"

const PaginationNext = ({
  className,
  ...props
}: React.ComponentProps<typeof PaginationLink>) => {
  const t = useAppT();
  return (
    <PaginationLink
      aria-label={t('ui.pagination.next')}
      size="default"
      className={cn("gap-1", className)}
      {...props}
    >
      <ChevronRight className="h-4 w-4" />
    </PaginationLink>
  )
}
PaginationNext.displayName = "PaginationNext"

const PaginationEllipsis = ({
  className,
  ...props
}: React.ComponentProps<"span">) => (
  <span
    aria-hidden
    className={cn("flex h-9 w-9 items-center justify-center", className)}
    {...props}
  >
    <MoreHorizontal className="h-4 w-4" />
    <span className="sr-only">More pages</span>
  </span>
)
PaginationEllipsis.displayName = "PaginationEllipsis"

export {
  Pagination,
  PaginationContent,
  PaginationLink,
  PaginationItem,
  PaginationPrevious,
  PaginationNext,
  PaginationEllipsis,
}
