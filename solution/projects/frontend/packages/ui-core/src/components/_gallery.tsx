/**
 * Shared layout for the per-group gallery pages.
 *
 * Individual stories answer "how does this component behave?". A gallery
 * answers the question they cannot: "what is in this group, and which of
 * these do I want?" — which only works when the options sit side by side at
 * the same size, in the same theme, on one screen.
 *
 * Lives in `_gallery.tsx` rather than a `.stories.tsx` so Storybook's glob
 * does not pick it up as a story of its own.
 */
import type { ReactNode } from 'react';

/** One labelled cell. `name` matches the exported symbol, so it is greppable. */
export function GalleryItem({
  name,
  hint,
  children,
}: {
  name: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <section className="flex min-w-0 flex-col gap-2">
      <header className="flex min-w-0 flex-col gap-0.5">
        <h3 className="font-mono text-sm font-medium">{name}</h3>
        {hint ? <p className="text-muted-foreground text-xs">{hint}</p> : null}
      </header>
      {/* min-w-0 throughout: a wide child (a full-width trigger, a long badge
          row) otherwise forces the grid track open and breaks the columns. */}
      <div className="min-w-0">{children}</div>
    </section>
  );
}

/**
 * Responsive grid of `GalleryItem`s.
 *
 * Auto-fit rather than a fixed column count — the same page has to read on a
 * docs iframe and on a full-width canvas, and a hard `grid-cols-3` squashes
 * triggers into unusability on the narrow one.
 */
export function Gallery({
  children,
  min = '18rem',
}: {
  children: ReactNode;
  /** Minimum track width before the grid drops a column. */
  min?: string;
}) {
  return (
    <div
      className="grid w-full gap-x-8 gap-y-7"
      style={{ gridTemplateColumns: `repeat(auto-fit, minmax(${min}, 1fr))` }}
    >
      {children}
    </div>
  );
}

/** Groups related items under a heading inside a gallery page. */
export function GallerySection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-4">
      <h2 className="text-muted-foreground text-xs font-semibold uppercase tracking-wide">
        {title}
      </h2>
      {children}
    </section>
  );
}

/** Page shell — vertical rhythm between sections. */
export function GalleryPage({ children }: { children: ReactNode }) {
  return <div className="flex w-full flex-col gap-10 p-1">{children}</div>;
}
