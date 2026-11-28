'use client';

/**
 * React-Router (v7) adapter — bridges our framework-agnostic router hooks
 * to `react-router` so SPA navigations flow through the data router
 * (`createBrowserRouter`) instead of the bare History API fallback.
 *
 * USAGE:
 *   Mount once INSIDE the router context — i.e. inside an element that
 *   `RouterProvider` renders (a layout-route element / `<Outlet/>` parent),
 *   NOT around `<RouterProvider>` itself (that subtree has no router context,
 *   so `useNavigate` would throw):
 *
 *   ```tsx
 *   import { ReactRouterProvider } from '@djangocfg/ui-core/adapters/react-router';
 *
 *   function Shell() {
 *     return (
 *       <ReactRouterProvider>
 *         <Layout><Outlet /></Layout>
 *       </ReactRouterProvider>
 *     );
 *   }
 *   ```
 *
 *   Without this provider, our hooks fall back to the History API adapter —
 *   which mutates `window.history` directly and bypasses React-Router's
 *   `<Outlet/>` swap, so programmatic `useNavigate` / `<Link>` clicks desync
 *   from the router. Mount it in any Vite / React-Router SPA.
 *
 * PEER DEPENDENCY:
 *   `react-router` is an OPTIONAL peer of @djangocfg/ui-core. The base package
 *   never imports from `react-router`. This sub-path entry does — so it only
 *   loads when the consumer explicitly imports `/adapters/react-router`.
 *   Next.js / non-RR consumers: don't import this file and `react-router` is
 *   never resolved.
 */

import { forwardRef, useMemo, type ReactNode } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router';

import {
  RouterAdapterProvider,
  type RouterAdapter,
  type RouterLocation,
} from '../adapter';
import {
  LinkProvider,
  type LinkComponent,
  type LinkComponentProps,
} from '../../../components/navigation/link';

const SSR_LOCATION: RouterLocation = Object.freeze({
  pathname: '/',
  search: '',
  hash: '',
});

export interface ReactRouterAdapterProps {
  children: ReactNode;
}

/**
 * Wraps a subtree so all `@djangocfg/ui-core/hooks` router calls go through
 * React-Router's data router. `back`/`forward` use the numeric-delta overload
 * of `useNavigate`; `getLocation` reads `window.location` (SSR-guarded).
 *
 * Must be rendered inside the router context (under `RouterProvider`), since
 * `useNavigate` requires it.
 */
export function ReactRouterAdapter({ children }: ReactRouterAdapterProps) {
  const navigate = useNavigate();

  const adapter = useMemo<RouterAdapter>(
    () => ({
      push(url) {
        navigate(url);
      },
      replace(url) {
        navigate(url, { replace: true });
      },
      back() {
        navigate(-1);
      },
      forward() {
        navigate(1);
      },
      getLocation() {
        if (typeof window === 'undefined') return SSR_LOCATION;
        return {
          pathname: window.location.pathname,
          search: window.location.search,
          hash: window.location.hash,
        };
      },
    }),
    [navigate]
  );

  return (
    <RouterAdapterProvider value={adapter}>{children}</RouterAdapterProvider>
  );
}

/**
 * Maps our agnostic Link API → react-router `<Link>` props. Lives at module
 * scope so the component identity is stable (avoids tree remounts on every
 * render). `href` → `to`; `replace` is forwarded; `prefetch` (a Next-shaped
 * boolean) and `scroll` have no `react-router` equivalent and are dropped.
 */
const ReactRouterLinkAdapter: LinkComponent = forwardRef<HTMLAnchorElement, LinkComponentProps>(
  function ReactRouterLinkAdapter({ href, replace, scroll: _scroll, prefetch: _prefetch, children, ...rest }, ref) {
    return (
      <RouterLink to={href} replace={replace} ref={ref} {...rest}>
        {children}
      </RouterLink>
    );
  }
);

export interface ReactRouterLinkProviderProps {
  children: ReactNode;
}

/**
 * Wires `<Link>` from `@djangocfg/ui-core/components` to react-router's
 * `<Link>`. Mount alongside `ReactRouterAdapter` (inside the router context)
 * so every ui-core `<Link>` drives client-side routing.
 */
export function ReactRouterLinkProvider({ children }: ReactRouterLinkProviderProps) {
  return <LinkProvider value={ReactRouterLinkAdapter}>{children}</LinkProvider>;
}

export interface ReactRouterProviderProps {
  children: ReactNode;
}

/**
 * Convenience composition of `ReactRouterAdapter` (navigation backend) and
 * `ReactRouterLinkProvider` (link component) — mount this ONE component inside
 * the router context to wire ui-core's whole navigation seam to React-Router.
 */
export function ReactRouterProvider({ children }: ReactRouterProviderProps) {
  return (
    <ReactRouterAdapter>
      <ReactRouterLinkProvider>{children}</ReactRouterLinkProvider>
    </ReactRouterAdapter>
  );
}
