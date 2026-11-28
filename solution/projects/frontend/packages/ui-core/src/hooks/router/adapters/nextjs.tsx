'use client';

/**
 * Next.js adapter — bridges our framework-agnostic router hooks
 * to `next/navigation` so server components, route loaders, and
 * `prefetch` all fire correctly.
 *
 * USAGE:
 *   Mount once near the root of the App Router tree, e.g. inside
 *   the locale layout's client provider stack:
 *
 *   ```tsx
 *   import { NextRouterAdapter } from '@djangocfg/ui-core/adapters/nextjs';
 *
 *   <I18nProvider locale={locale} messages={messages}>
 *     <NextRouterAdapter>
 *       <AppLayout>{children}</AppLayout>
 *     </NextRouterAdapter>
 *   </I18nProvider>
 *   ```
 *
 *   Without this provider, our hooks fall back to the History API
 *   adapter — which works in plain SPAs (Wails, Electron, Vite, CRA)
 *   but in Next.js means: no server component refetch on navigation,
 *   no route loader, no prefetch. So always mount it in Next apps.
 *
 * PEER DEPENDENCY:
 *   `next` is an OPTIONAL peer of @djangocfg/ui-core. The base package
 *   never imports from `next/*`. This sub-path entry does — so it only
 *   loads when the consumer explicitly imports `/adapters/nextjs`.
 *   Wails / Electron consumers: don't import this file and `next` is
 *   never resolved.
 */

import {
  forwardRef,
  useEffect,
  useMemo,
  useRef,
  type AnchorHTMLAttributes,
  type ComponentType,
  type ReactNode,
  type Ref,
} from 'react';
import { usePathname, useRouter as useNextRouter } from 'next/navigation';
import NextLink from 'next/link';

import {
  RouterAdapterProvider,
  type RouterAdapter,
  type RouterLocation,
  type RouterNavigateOptions,
  writeUrlShallow,
} from '../adapter';
import { useRouteProgress } from '../../../route-progress';
import { shouldStartProgress } from '../../../route-progress/provider/shouldStart';
import { NAVIGATE_EVENT, patchHistoryOnce } from '../useLocation';
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

/** `url` resolved against the current page; `null` outside the browser or for an unparsable url. */
function resolve(url: string): URL | null {
  if (typeof window === 'undefined') return null;
  try {
    return new URL(url, window.location.href);
  } catch {
    return null;
  }
}

export interface NextRouterAdapterProps {
  children: ReactNode;
  /**
   * Pass `scroll: false` to every Next router call by default.
   * Useful for filter/pagination apps where the page should never
   * jump on URL changes. Default: undefined (use Next's own default).
   */
  defaultScroll?: boolean;
}

/**
 * Wraps a subtree so all `@djangocfg/ui-core/hooks` router calls go
 * through Next's App Router. Server components, loaders, and prefetch
 * keep working as if you used `next/navigation` directly.
 */
export function NextRouterAdapter({ children, defaultScroll }: NextRouterAdapterProps) {
  const next = useNextRouter();
  const pathname = usePathname();
  // The top bar and the page switches live in `RouteProgressProvider` (BaseApp mounts it); without one this adapter shows no bar.
  const progress = useRouteProgress();
  const progressRef = useRef(progress);
  progressRef.current = progress;

  // Every committed navigation ends the bar: Next's `pushState`/`replaceState` on commit, or a new pathname.
  useEffect(() => {
    patchHistoryOnce();
    const stop = () => progressRef.current?.engine.done();
    window.addEventListener(NAVIGATE_EVENT, stop);
    return () => window.removeEventListener(NAVIGATE_EVENT, stop);
  }, []);
  // Next's App Router commits its own navigations through the `pushState` it captured at boot, before our patch, so
  // `NAVIGATE_EVENT` never fires for them. Announce every new pathname ourselves: `usePathnameChange`, `useLocation` and
  // any other subscriber then see a Next navigation like any other (seen on gptkino 2026-11-11: the phone assistant
  // stayed open after a link). The first pathname is not a navigation.
  const firstPathname = useRef(true);
  useEffect(() => {
    progressRef.current?.engine.done();
    if (firstPathname.current) {
      firstPathname.current = false;
      return;
    }
    window.dispatchEvent(new Event(NAVIGATE_EVENT));
  }, [pathname]);

  const adapter = useMemo<RouterAdapter>(
    () => {
      // Priority for scroll: the call, then the page (`useNavigationBehavior`), then `defaultScroll`, then Next's own default.
      const nextOptions = (opts?: RouterNavigateOptions) => {
        const scroll = opts?.scroll ?? progressRef.current?.behavior.get().scroll ?? defaultScroll;
        return scroll === undefined ? undefined : { scroll };
      };
      const startBar = (url: string, opts?: RouterNavigateOptions) => {
        const to = resolve(url);
        if (to && shouldStartProgress(progressRef.current, new URL(window.location.href), to, opts?.progress)) {
          progressRef.current?.engine.start();
        }
      };
      return {
      push(url, opts) {
        startBar(url, opts);
        next.push(url, nextOptions(opts));
      },
      replace(url, opts) {
        startBar(url, opts);
        next.replace(url, nextOptions(opts));
      },
      // No router call: no RSC request, no bar, no scroll. `null` state so Next syncs `useSearchParams`.
      shallow(url, opts) {
        writeUrlShallow(url, opts?.replace ?? false);
      },
      back() {
        next.back();
      },
      forward() {
        next.forward();
      },
      getLocation() {
        if (typeof window === 'undefined') return SSR_LOCATION;
        return {
          pathname: window.location.pathname,
          search: window.location.search,
          hash: window.location.hash,
        };
      },
      };
    },
    [next, defaultScroll]
  );

  return (
    <RouterAdapterProvider value={adapter}>{children}</RouterAdapterProvider>
  );
}

/**
 * Maps our agnostic Link API → next/link props. Lives at module scope so
 * the component identity is stable (avoids tree remounts on every render).
 */
const NextLinkAdapter: LinkComponent = forwardRef<HTMLAnchorElement, LinkComponentProps>(
  function NextLinkAdapter({ href, replace, scroll, prefetch, children, ...rest }, ref) {
    return (
      <NextLink
        href={href}
        replace={replace}
        scroll={scroll}
        prefetch={prefetch ?? undefined}
        ref={ref}
        {...rest}
      >
        {children}
      </NextLink>
    );
  }
);

export interface NextLinkProviderProps {
  children: ReactNode;
}

/**
 * Wires `<Link>` from `@djangocfg/ui-core/components` to `next/link`.
 * Mount alongside `NextRouterAdapter` near the root of a Next app so
 * every Link picks up Next's prefetch / RSC handling automatically.
 */
export function NextLinkProvider({ children }: NextLinkProviderProps) {
  return <LinkProvider value={NextLinkAdapter}>{children}</LinkProvider>;
}

/**
 * Minimal shape of the `Link` returned by next-intl's `createNavigation()`.
 * Typed structurally so we don't take a peer dep on `next-intl`.
 */
type NextIntlLinkLike = ComponentType<
  AnchorHTMLAttributes<HTMLAnchorElement> & {
    href: string;
    locale?: string;
    replace?: boolean;
    scroll?: boolean;
    prefetch?: boolean | null;
    ref?: Ref<HTMLAnchorElement>;
  }
>;

/**
 * Wraps next-intl's `Link` (from `createNavigation()`) into our generic
 * `LinkComponent`, so apps using `next-intl` get locale-prefixed hrefs on
 * every `<Link>` rendered through `@djangocfg/ui-core`.
 *
 * Pass the result as `baseApp.linkAdapter` to `AppLayout` / `BaseApp` —
 * it overrides the default `next/link` adapter for the whole subtree.
 *
 * @example
 *   import { createNextIntlLinkAdapter } from '@djangocfg/ui-core/adapters/nextjs';
 *   import { Link as IntlLink } from '@/i18n/navigation';
 *
 *   const linkAdapter = useMemo(() => createNextIntlLinkAdapter(IntlLink), []);
 *   <AppLayout baseApp={{ ..., linkAdapter }} />
 */
export function createNextIntlLinkAdapter(
  NextIntlLink: NextIntlLinkLike,
): LinkComponent {
  return forwardRef<HTMLAnchorElement, LinkComponentProps>(
    function NextIntlLinkAdapter({ href, replace, scroll, prefetch, children, ...rest }, ref) {
      return (
        <NextIntlLink
          href={href}
          replace={replace}
          scroll={scroll}
          prefetch={prefetch}
          ref={ref}
          {...rest}
        >
          {children}
        </NextIntlLink>
      );
    },
  );
}
