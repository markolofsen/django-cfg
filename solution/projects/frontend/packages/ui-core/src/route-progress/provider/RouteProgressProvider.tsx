'use client';

import { useEffect, useMemo, useRef, type ReactNode } from 'react';

import { createNavigationBehaviorStore } from '../behavior/store';
import { createProgressEngine } from '../engine/createProgressEngine';
import type { ProgressEngineOptions } from '../engine/types';
import { attachRouteProgressTriggers } from '../triggers/attach';
import { RouteProgressBar } from '../view/RouteProgressBar';
import { RouteProgressContext, type RouteProgressContextValue } from './context';
import { shouldStartProgress } from './shouldStart';

export interface RouteProgressProviderProps extends ProgressEngineOptions {
  children: ReactNode;
  /** `false` turns the bar off for the whole app. Default true. */
  enabled?: boolean;
  /**
   * Route rule for the whole app, replacing the default "the pathname changes".
   * A page's `useNavigationBehavior({ progress: false })` and a call's `progress` option still win.
   */
  shouldShow?: (from: URL, to: URL) => boolean;
  /** CSS colour of the bar. */
  color?: string;
  /** Height of the bar in px. */
  height?: number;
}

/**
 * One progress engine and one behaviour store for the app. Mounts the bar and the link-click
 * triggers. The router wiring (`NextRouterAdapter`) starts it for programmatic navigation and
 * ends every run when the navigation commits.
 */
export function RouteProgressProvider({
  children,
  enabled = true,
  shouldShow,
  color,
  height,
  ...engineOptions
}: RouteProgressProviderProps) {
  const { minimum, trickleMs, maxMs, finishMs } = engineOptions;
  // One instance per mount; the options only matter the first time.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const engine = useMemo(() => createProgressEngine({ minimum, trickleMs, maxMs, finishMs }), []);
  const behavior = useMemo(createNavigationBehaviorStore, []);

  const value = useMemo<RouteProgressContextValue>(
    () => ({ engine, behavior, enabled, shouldShow }),
    [engine, behavior, enabled, shouldShow],
  );

  // The triggers read the latest value, so an inline `shouldShow` never re-attaches them (which would cancel a running bar).
  const latest = useRef(value);
  latest.current = value;

  useEffect(() => {
    if (!enabled) return;
    const detach = attachRouteProgressTriggers({
      engine,
      shouldStart: (from, to) => shouldStartProgress(latest.current, from, to),
    });
    return () => {
      detach();
      engine.cancel();
    };
  }, [engine, enabled]);

  return (
    <RouteProgressContext.Provider value={value}>
      {children}
      {enabled && <RouteProgressBar engine={engine} color={color} height={height} />}
    </RouteProgressContext.Provider>
  );
}
