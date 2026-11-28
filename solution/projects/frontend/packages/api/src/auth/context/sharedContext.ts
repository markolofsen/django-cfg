import { createContext, type Context } from 'react';

/**
 * A React context that stays ONE object even when the bundle holds several copies of this package.
 *
 * pnpm builds a separate physical copy of a package per distinct peer set, and a dual ESM/CJS load can do the same.
 * Each copy would call `createContext` itself: the provider mounted from copy A and a `useAuth()` called from copy B
 * would then never meet, B would read the empty default and the page guard would redirect a signed-in user forever
 * (hub.reforms.ai, 5 Nov 2026). Registering the context on `globalThis` makes every copy share it. React itself must
 * still be a single copy, which every Next.js app already requires.
 */
export function sharedContext<T>(key: string, initial: T): Context<T> {
  const g = globalThis as Record<string, unknown>;
  const registry = (g.__cfgAuthContexts ??= {}) as Record<string, Context<unknown>>;
  return (registry[key] ??= createContext<unknown>(initial)) as Context<T>;
}
