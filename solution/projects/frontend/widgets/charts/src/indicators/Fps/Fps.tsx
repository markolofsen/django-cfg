'use client';

import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { cn } from '@djangocfg/ui-core/lib';
import { fpsVariants } from './types';
import type { FpsProps } from './types';

export function Fps(props: FpsProps) {
  const {
    strategy = 'fixed',
    position = 'top-right',
    label,
    updateInterval = 500,
    warningThreshold = 30,
    errorThreshold = 20,
    portalContainer: portalContainerProp,
    enabled = true,
    className,
    ...fpsProps
  } = props;

  const [mounted, setMounted] = React.useState(false);
  const [fps, setFps] = React.useState(0);
  const frameCountRef = React.useRef(0);
  const lastTimeRef = React.useRef(performance.now());
  const animationFrameRef = React.useRef<number | null>(null);

  React.useLayoutEffect(() => setMounted(true), []);

  const status = React.useMemo(() => {
    if (fps < errorThreshold) return 'error';
    if (fps < warningThreshold) return 'warning';
    return 'good';
  }, [fps, errorThreshold, warningThreshold]);

  React.useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;

    function measureFps() {
      const now = performance.now();
      const delta = now - lastTimeRef.current;
      frameCountRef.current += 1;

      if (delta >= updateInterval) {
        const currentFps = Math.round((frameCountRef.current * 1000) / delta);
        setFps(currentFps);
        frameCountRef.current = 0;
        lastTimeRef.current = now;
      }

      animationFrameRef.current = requestAnimationFrame(measureFps);
    }

    animationFrameRef.current = requestAnimationFrame(measureFps);

    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [enabled, updateInterval]);

  if (!enabled) return null;

  const portalContainer =
    strategy === 'absolute'
      ? null
      : (portalContainerProp ?? (mounted ? globalThis.document?.body : null));

  const Comp = (
    <div
      aria-hidden="true"
      data-slot="fps"
      {...fpsProps}
      className={cn(fpsVariants({ strategy, position, status }), className)}
    >
      {label && (
        <span data-slot="fps-label" className="text-muted-foreground">
          {label}:
        </span>
      )}
      <span data-slot="fps-value">{fps}</span>
    </div>
  );

  return portalContainer ? ReactDOM.createPortal(Comp, portalContainer) : Comp;
}

Fps.displayName = 'Fps';
