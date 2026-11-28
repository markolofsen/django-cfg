'use client';

/**
 * NextIntlLinkBridge
 *
 * Bridges next-intl's locale-aware `Link` (built from a `routing` object via
 * `createNavigation()`) into our framework-agnostic `LinkProvider`. Mounted
 * by `BaseApp` only when the consumer passes `i18n.routing`.
 *
 * Why this lives in @djangocfg/layouts (not @djangocfg/ui-core):
 *   ui-core stays free of next-intl. Layouts already depend on next + nextjs
 *   plumbing, so taking a peer on next-intl here is honest about scope and
 *   keeps consumer apps from having to wire `createNavigation` themselves.
 */

import { forwardRef, useMemo, type ReactNode } from 'react';
import { createNavigation } from 'next-intl/navigation';

import {
  LinkProvider,
  type LinkComponent,
  type LinkComponentProps,
} from '@djangocfg/ui-core/components';

import type { NextIntlRouting } from '../types/layout.types';

export interface NextIntlLinkBridgeProps {
  /** The `routing` object returned by `defineRouting()` from `next-intl/routing`. */
  routing: NextIntlRouting;
  children: ReactNode;
}

export function NextIntlLinkBridge({ routing, children }: NextIntlLinkBridgeProps) {
  const adapter = useMemo<LinkComponent>(() => {
    // The `createNavigation` overload signature splits between localized and
    // shared routing variants and TS can't narrow either way through our
    // opaque `NextIntlRouting` alias — cast to satisfy the localized branch
    // and rely on next-intl to handle both at runtime.
    const { Link: IntlLink } = createNavigation(
      routing as unknown as Parameters<typeof createNavigation>[0],
    );
    return forwardRef<HTMLAnchorElement, LinkComponentProps>(
      function NextIntlLinkAdapter(
        { href, replace, scroll, prefetch, children: kids, ...rest },
        ref,
      ) {
        // next-intl's Link accepts the same props we expose. The cast is safe
        // because LinkComponentProps is a structural subset.
        const Link = IntlLink as unknown as LinkComponent;
        return (
          <Link
            href={href}
            replace={replace}
            scroll={scroll}
            prefetch={prefetch}
            ref={ref}
            {...rest}
          >
            {kids}
          </Link>
        );
      },
    );
  }, [routing]);

  return <LinkProvider value={adapter}>{children}</LinkProvider>;
}
