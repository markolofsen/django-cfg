'use client';

/**
 * <Link> — framework-agnostic link component.
 *
 * WHY:
 *   We want a single Link import everywhere, regardless of whether the
 *   host app is Next.js, Wails, Electron, Vite, or plain CRA. When a
 *   framework adapter is mounted (e.g. NextLinkProvider) the native
 *   component handles prefetch / locale / RSC wiring. Otherwise we
 *   render a plain <a> and route clicks through the active router
 *   adapter (which itself defaults to History API).
 *
 *   Behavior parity with `<a>`:
 *     - Cmd/Ctrl/Shift+click and middle-click open a new tab natively
 *       (we let the browser handle modifier clicks — DON'T preventDefault).
 *     - External / non-internal hrefs (http://, mailto:, tel:, target=_blank)
 *       skip SPA nav entirely and behave as the browser would.
 *
 * @example
 *   import { Link } from '@djangocfg/ui-core/components';
 *   <Link href="/dashboard">Dashboard</Link>
 *   <Link href="/dashboard" replace scroll>Reset</Link>
 *   <Link href="https://example.com" target="_blank" rel="noopener noreferrer">External</Link>
 */

import { forwardRef, useCallback, type AnchorHTMLAttributes, type MouseEvent, type ReactNode } from 'react';
import { useNavigate } from '../../../hooks/router/useNavigate';
import { useLinkComponent } from './LinkContext';

type AnchorProps = Omit<
  AnchorHTMLAttributes<HTMLAnchorElement>,
  'href' | 'onClick'
>;

export interface LinkProps extends AnchorProps {
  href: string;
  /** Use replaceState instead of pushState. Default: false. */
  replace?: boolean;
  /** Scroll to top after SPA navigation. Default: false. */
  scroll?: boolean;
  /**
   * Hint for the host framework's prefetcher (Next.js).
   * Ignored by the agnostic fallback.
   */
  prefetch?: boolean | null;
  children?: ReactNode;
  onClick?: (event: MouseEvent<HTMLAnchorElement>) => void;
}

/** True for protocols / schemes the browser must handle natively. */
function isExternalHref(href: string): boolean {
  // Allow same-origin absolute paths (`/foo`, `./foo`, `#hash`, `?q=1`).
  if (href.startsWith('/') && !href.startsWith('//')) return false;
  if (href.startsWith('#') || href.startsWith('?')) return false;
  // Anything with a scheme (http:, https:, mailto:, tel:, ipfs:, …).
  if (/^[a-z][a-z0-9+.-]*:/i.test(href)) return true;
  // `//example.com` protocol-relative.
  if (href.startsWith('//')) return true;
  return false;
}

/**
 * True when the click should be left to the browser:
 * modifier keys, non-primary mouse button, or `target=_blank`.
 */
function shouldBypassClick(event: MouseEvent<HTMLAnchorElement>, target?: string): boolean {
  if (event.defaultPrevented) return true;
  if (event.button !== 0) return true;
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return true;
  if (target && target !== '' && target !== '_self') return true;
  return false;
}

export const Link = forwardRef<HTMLAnchorElement, LinkProps>(function Link(
  { href, replace, scroll, prefetch, target, rel, onClick, children, ...rest },
  ref
) {
  const Adapter = useLinkComponent();
  const { navigate } = useNavigate();

  const handleClick = useCallback(
    (event: MouseEvent<HTMLAnchorElement>) => {
      onClick?.(event);
      if (event.defaultPrevented) return;
      if (isExternalHref(href)) return;
      if (shouldBypassClick(event, target)) return;
      event.preventDefault();
      navigate(href, { replace, scroll });
    },
    [onClick, href, target, navigate, replace, scroll]
  );

  if (Adapter) {
    return (
      <Adapter
        href={href}
        replace={replace}
        scroll={scroll}
        prefetch={prefetch}
        target={target}
        rel={rel}
        ref={ref}
        onClick={onClick}
        {...rest}
      >
        {children}
      </Adapter>
    );
  }

  return (
    <a
      href={href}
      target={target}
      rel={rel}
      ref={ref}
      onClick={handleClick}
      {...rest}
    >
      {children}
    </a>
  );
});
