'use client';

/**
 * LinkContext
 *
 * Adapter slot for the framework's native link component (e.g. `next/link`).
 * `<Link>` reads this context: when populated, it delegates rendering so
 * the host framework's prefetching / locale handling kicks in. When empty,
 * `<Link>` falls back to a pure `<a>` driven by `useNavigate`.
 *
 * Mount once near the root via the matching adapter
 * (e.g. `NextLinkProvider` from `@djangocfg/ui-core/adapters/nextjs`).
 */

import { createContext, useContext, type ComponentType, type ReactNode, type Ref } from 'react';

export interface LinkComponentProps {
  href: string;
  replace?: boolean;
  scroll?: boolean;
  prefetch?: boolean | null;
  className?: string;
  children?: ReactNode;
  target?: string;
  rel?: string;
  ref?: Ref<HTMLAnchorElement>;
  onClick?: (event: React.MouseEvent<HTMLAnchorElement>) => void;
  [dataAttr: `data-${string}`]: unknown;
  [ariaAttr: `aria-${string}`]: unknown;
}

export type LinkComponent = ComponentType<LinkComponentProps>;

/**
 * Keyed on a global rather than a module-local `createContext`.
 *
 * A consumer reaches this module by two specifiers — the package root (which
 * re-exports `<Link>`) and the `/adapters/*` subpath (which mounts the
 * provider). A bundler may instantiate the module once per specifier, giving
 * two distinct context objects: the provider fills one, `<Link>` reads the
 * other, and every link silently falls back to the History-API `<a>`.
 *
 * The failure is invisible — the URL still changes — so the host framework's
 * router is simply never told, and the app renders the previous route until
 * something else forces a re-render. Sharing one object through the global
 * makes the two instances agree whatever the bundler decides.
 */
const CONTEXT_KEY = Symbol.for('@djangocfg/ui-core.LinkComponentContext');
// `typeof globalThis` carries no index signature, but the object genuinely
// accepts symbol keys — this asserts a property the runtime has.
const globalScope = globalThis as Record<symbol, unknown>;

export const LinkComponentContext =
  (globalScope[CONTEXT_KEY] as ReturnType<typeof createContext<LinkComponent | null>> | undefined) ??
  (globalScope[CONTEXT_KEY] = createContext<LinkComponent | null>(null));

export interface LinkProviderProps {
  value: LinkComponent;
  children: ReactNode;
}

export function LinkProvider({ value, children }: LinkProviderProps) {
  return (
    <LinkComponentContext.Provider value={value}>
      {children}
    </LinkComponentContext.Provider>
  );
}

/** Returns the host-framework Link if a provider is mounted, else `null`. */
export function useLinkComponent(): LinkComponent | null {
  return useContext(LinkComponentContext);
}
