/**
 * What the app currently allows navigation to do: the scroll jump to the top and the top
 * loading bar. Pages and sections hold a lease for as long as they are mounted; the latest
 * lease that sets a field decides it. One store per app, created by the provider: no global.
 */

export interface NavigationBehavior {
  /** `false`: do not scroll to the top on navigation. */
  scroll?: boolean;
  /** `false`: do not show the top loading bar. */
  progress?: boolean;
}

export interface NavigationBehaviorStore {
  /** The effective behaviour. Same object until a lease changes. */
  get(): NavigationBehavior;
  subscribe(listener: () => void): () => void;
  /** Take a lease; returns the function that gives it back. */
  acquire(lease: NavigationBehavior): () => void;
}

export function createNavigationBehaviorStore(): NavigationBehaviorStore {
  const leases: NavigationBehavior[] = [];
  const listeners = new Set<() => void>();
  let current: NavigationBehavior = {};

  const recompute = () => {
    const next: NavigationBehavior = {};
    for (const l of leases) {
      if (l.scroll !== undefined) next.scroll = l.scroll;
      if (l.progress !== undefined) next.progress = l.progress;
    }
    if (next.scroll === current.scroll && next.progress === current.progress) return;
    current = next;
    listeners.forEach((fn) => fn());
  };

  return {
    get: () => current,
    subscribe(listener) {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
    acquire(lease) {
      const own = { ...lease };
      leases.push(own);
      recompute();
      return () => {
        const i = leases.indexOf(own);
        if (i === -1) return;
        leases.splice(i, 1);
        recompute();
      };
    },
  };
}
