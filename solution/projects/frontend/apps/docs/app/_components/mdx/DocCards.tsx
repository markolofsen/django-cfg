import type { ReactNode } from 'react';

/**
 * Vercel-style doc cards. Replaces Nextra's built-in <Cards>/<Card> whose
 * hybrid title+children layout renders the title in a bottom slot. Here the
 * title is always on top (bold), description below, with consistent padding.
 * Styling is plain CSS (.doc-cards / .doc-card) in app/_core/styles/ so it
 * doesn't depend on Nextra's internal `x:` utilities.
 */

export function DocCards({ children }: { children: ReactNode }) {
  return <div className="doc-cards">{children}</div>;
}

export function DocCard({
  title,
  href,
  icon,
  children,
}: {
  title?: ReactNode;
  href?: string;
  icon?: ReactNode;
  children?: ReactNode;
}) {
  const external = typeof href === 'string' && href.startsWith('http');
  const target = external ? '_blank' : undefined;
  const rel = external ? 'noreferrer' : undefined;
  return (
    <a className="doc-card" href={href} target={target} rel={rel}>
      <span className="doc-card__head">
        {icon ? <span className="doc-card__icon">{icon}</span> : null}
        <span className="doc-card__title">{title}</span>
        <span className="doc-card__arrow" aria-hidden>
          →
        </span>
      </span>
      {children ? <span className="doc-card__body">{children}</span> : null}
    </a>
  );
}
