'use client';

import { useSyncExternalStore } from 'react';

import type { ProgressEngine } from '../engine/types';
import { useReducedMotion } from './useReducedMotion';

export interface RouteProgressBarProps {
  engine: ProgressEngine;
  /** CSS colour. Default: the `--route-progress-color` variable, else `--primary`. */
  color?: string;
  /** Height in px. Default 3. */
  height?: number;
}

const serverState = { phase: 'idle', value: 0 } as const;

/**
 * The thin bar at the top of the window. Decoration only (`aria-hidden`): the page owns its
 * own busy semantics. Styling hooks: `--route-progress-color`, `--route-progress-height`,
 * `--route-progress-z`. Renders nothing while idle and on the server.
 */
export function RouteProgressBar({ engine, color, height = 3 }: RouteProgressBarProps) {
  const state = useSyncExternalStore(engine.subscribe, engine.getState, () => serverState);
  const reduced = useReducedMotion();
  if (state.phase === 'idle') return null;

  const finishing = state.phase === 'finishing';
  const fill = reduced ? 'none' : 'transform 200ms ease';
  const fade = reduced ? 'opacity 150ms linear' : 'opacity 300ms ease 100ms';
  const bar = color ?? 'var(--route-progress-color, var(--primary))';

  return (
    <div
      aria-hidden
      data-route-progress={state.phase}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: `var(--route-progress-height, ${height}px)`,
        zIndex: 'var(--route-progress-z, 1600)' as unknown as number,
        pointerEvents: 'none',
        opacity: finishing ? 0 : 1,
        transition: fade,
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: bar,
          transformOrigin: 'left center',
          transform: `scaleX(${state.value})`,
          transition: fill,
          boxShadow: reduced ? 'none' : `0 0 10px ${bar}, 0 0 5px ${bar}`,
        }}
      />
    </div>
  );
}
