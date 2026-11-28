import * as React from 'react';

import { cn } from '../../../lib/utils';

const Table = React.forwardRef<
  HTMLTableElement,
  React.HTMLAttributes<HTMLTableElement> & {
    containerClassName?: string
    /**
     * Wrap the table in the card-style frame (border + radius + `--card`
     * surface). Default `true` — a standalone `<Table>` reads as a contained
     * data panel against the page background. Set `false` when an outer
     * container (e.g. `DataTable`) already supplies the frame, to avoid a
     * double border and a radius that doesn't match the parent's.
     */
    frame?: boolean
    /**
     * A database grid, as in Notion: no header band, hairline column dividers, 36px rows,
     * regular-weight column labels. Pair with `frame={false}` on a page-level table.
     */
    grid?: boolean
  }
>(({ className, containerClassName, frame = true, grid = false, ...props }, ref) => {
  // Scroll container. Cap its height via `containerClassName`
  // (e.g. "max-h-80") to get a scrollable body with a sticky header.
  const scroll = (
    <div className={cn("w-full overflow-auto", containerClassName)}>
      <table
        ref={ref}
        className={cn(
          "w-full caption-bottom text-sm",
          grid &&
            "[&_thead]:bg-transparent [&_th]:h-8 [&_th]:border-r [&_th]:border-divider [&_th]:font-normal [&_td]:h-9 [&_td]:border-r [&_td]:border-divider [&_td]:py-0 [&_th:last-child]:border-r-0 [&_td:last-child]:border-r-0",
          className
        )}
        {...props}
      />
    </div>
  )

  if (!frame) return scroll

  // Card-style frame: matches ui-core `Card` (`--radius-popover` corner +
  // `--shadow-card`) so a standalone table reads as the same kind of contained
  // panel as every other surface in the app — the page `--background` alone
  // gives no separation. `overflow-hidden` clips the header band and row
  // borders to the rounded corners.
  return (
    <div className="relative w-full overflow-hidden rounded-[var(--radius-popover)] border border-border bg-card text-card-foreground [box-shadow:var(--shadow-card)]">
      {scroll}
    </div>
  )
})
Table.displayName = "Table"

const TableHeader = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement> & { sticky?: boolean }
>(({ className, sticky = false, ...props }, ref) => (
  // The header band KEEPS `--border`: it divides labels from data, which is a
  // structural edge rather than one row from the next. Frame and header are
  // the two strong lines; everything between rows is quieter.
  // Tinted header band with a solid bottom border so the column labels
  // separate clearly from the body in both light and dark.
  // When `sticky`, the band must be fully opaque (solid `bg-muted`, not the
  // /50 tint) so scrolled body rows don't bleed through it.
  <thead
    ref={ref}
    className={cn(
      "[&_tr]:border-b [&_tr]:border-border",
      sticky ? "sticky top-0 z-10 bg-muted" : "bg-muted/50",
      className
    )}
    {...props}
  />
))
TableHeader.displayName = "TableHeader"

const TableBody = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement> & { striped?: boolean }
>(({ className, striped = false, ...props }, ref) => (
  // `striped` opts into zebra rows via a structural selector on the body, so
  // callers don't have to compute `i % 2` per row. Keeps the headless API:
  // per-row className still wins and the default (false) is unchanged.
  <tbody
    ref={ref}
    className={cn(
      "[&_tr:last-child]:border-0",
      striped && "[&_tr:nth-child(even)]:bg-muted/50",
      className
    )}
    {...props}
  />
))
TableBody.displayName = "TableBody"

const TableFooter = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tfoot
    ref={ref}
    className={cn(
      "border-t bg-muted/50 font-medium [&>tr]:last:border-b-0",
      className
    )}
    {...props}
  />
))
TableFooter.displayName = "TableFooter"

const TableRow = React.forwardRef<
  HTMLTableRowElement,
  React.HTMLAttributes<HTMLTableRowElement> & { key?: React.Key }
>(({ className, ...props }, ref) => (
  <tr
    ref={ref}
    className={cn(
      // `--divider`, not `--border`. A row separator lives INSIDE the panel, so
      // it must read as weaker than the frame around it; both drawing
      // `--border` made five internal lines shout as loudly as the one edge,
      // and the table read as a grid of boxes rather than a list.
      "border-b border-divider transition-colors hover:bg-muted/50 data-[state=selected]:bg-accent",
      className
    )}
    {...props}
  />
))
TableRow.displayName = "TableRow"

const TableHead = React.forwardRef<
  HTMLTableCellElement,
  React.ThHTMLAttributes<HTMLTableCellElement> & { key?: React.Key }
>(({ className, ...props }, ref) => (
  <th
    ref={ref}
    className={cn(
      "h-10 px-2 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
      className
    )}
    {...props}
  />
))
TableHead.displayName = "TableHead"

const TableCell = React.forwardRef<
  HTMLTableCellElement,
  React.TdHTMLAttributes<HTMLTableCellElement> & { key?: React.Key }
>(({ className, ...props }, ref) => (
  <td
    ref={ref}
    className={cn(
      "p-2 align-middle [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
      className
    )}
    {...props}
  />
))
TableCell.displayName = "TableCell"

const TableCaption = React.forwardRef<
  HTMLTableCaptionElement,
  React.HTMLAttributes<HTMLTableCaptionElement>
>(({ className, ...props }, ref) => (
  // Caption sits at the bottom inside the card frame; a top border + padding
  // make it read as a footer strip rather than floating text.
  <caption
    ref={ref}
    className={cn(
      "border-t border-border px-3 py-2.5 text-left text-sm text-muted-foreground",
      className
    )}
    {...props}
  />
))
TableCaption.displayName = "TableCaption"

export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
}
