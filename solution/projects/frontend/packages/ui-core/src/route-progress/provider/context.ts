'use client';

import { createContext, useContext } from 'react';

import type { NavigationBehaviorStore } from '../behavior/store';
import type { ProgressEngine } from '../engine/types';

export interface RouteProgressContextValue {
  engine: ProgressEngine;
  behavior: NavigationBehaviorStore;
  /** `false`: the app turned the bar off; nothing starts it. */
  enabled: boolean;
  /** App-level route rule, see `RouteProgressProvider`. */
  shouldShow?: (from: URL, to: URL) => boolean;
}

export const RouteProgressContext = createContext<RouteProgressContextValue | null>(null);

/** The app's engine and behaviour store, or `null` outside a `RouteProgressProvider`. */
export function useRouteProgress(): RouteProgressContextValue | null {
  return useContext(RouteProgressContext);
}
