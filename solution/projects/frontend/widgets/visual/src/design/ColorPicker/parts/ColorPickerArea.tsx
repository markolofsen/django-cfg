'use client';

import * as React from 'react';
import { useComposedRefs } from '@djangocfg/ui-core/lib';
import { cn } from '@djangocfg/ui-core/lib';
import { useColorPickerContext } from '../context/ColorPickerContext';
import { useStoreContext } from '../context/ColorPickerStore';
import { useStore } from '../context/ColorPickerStore';
import { hsvToRgb } from '../lib/color-utils';
import type { HSVColorValue } from '../types';

const AREA_NAME = 'ColorPickerArea';

// No `asChild`: the area owns pointer capture and its own geometry, so it
// cannot delegate its element to a caller's.
export function ColorPickerArea(props: React.ComponentProps<'div'>) {
  const {
    onPointerDown: onPointerDownProp,
    onPointerMove: onPointerMoveProp,
    onPointerUp: onPointerUpProp,
    className,
    ref,
    ...areaProps
  } = props;

  const propsRef = React.useRef({
    onPointerDown: onPointerDownProp,
    onPointerMove: onPointerMoveProp,
    onPointerUp: onPointerUpProp,
  });
  React.useEffect(() => {
    propsRef.current = {
      onPointerDown: onPointerDownProp,
      onPointerMove: onPointerMoveProp,
      onPointerUp: onPointerUpProp,
    };
  });

  const context = useColorPickerContext(AREA_NAME);
  const store = useStoreContext(AREA_NAME);

  const hsv = useStore((state) => state.hsv);

  const isDraggingRef = React.useRef(false);
  const areaRef = React.useRef<HTMLDivElement>(null);
  const composedRef = useComposedRefs(ref, areaRef);

  const updateColorFromPosition = React.useCallback(
    (clientX: number, clientY: number) => {
      if (!areaRef.current) return;

      const rect = areaRef.current.getBoundingClientRect();
      const x = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
      const y = Math.max(
        0,
        Math.min(1, 1 - (clientY - rect.top) / rect.height),
      );

      const newHsv: HSVColorValue = {
        h: hsv?.h ?? 0,
        s: Math.round(x * 100),
        v: Math.round(y * 100),
        a: hsv?.a ?? 1,
      };

      store.setHsv(newHsv);
      store.setColor(hsvToRgb(newHsv));
    },
    [hsv, store],
  );

  const onPointerDown = React.useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      if (context.disabled) return;
      propsRef.current.onPointerDown?.(event);
      if (event.defaultPrevented) return;

      isDraggingRef.current = true;
      areaRef.current?.setPointerCapture(event.pointerId);
      updateColorFromPosition(event.clientX, event.clientY);
    },
    [context.disabled, updateColorFromPosition],
  );

  const onPointerMove = React.useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      propsRef.current.onPointerMove?.(event);
      if (event.defaultPrevented) return;

      if (isDraggingRef.current) {
        updateColorFromPosition(event.clientX, event.clientY);
      }
    },
    [updateColorFromPosition],
  );

  const onPointerUp = React.useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      propsRef.current.onPointerUp?.(event);
      if (event.defaultPrevented) return;

      isDraggingRef.current = false;
      areaRef.current?.releasePointerCapture(event.pointerId);
    },
    [],
  );

  const hue = hsv?.h ?? 0;
  const backgroundHue = hsvToRgb({ h: hue, s: 100, v: 100, a: 1 });

  return (
    <div
      data-slot="color-picker-area"
      {...areaProps}
      className={cn(
        'relative h-40 w-full cursor-crosshair touch-none rounded-sm border',
        context.disabled && 'pointer-events-none opacity-50',
        className,
      )}
      ref={composedRef}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
    >
      <div className="absolute inset-0 overflow-hidden rounded-sm">
        <div
          className="absolute inset-0"
          style={{
            backgroundColor: `rgb(${backgroundHue.r}, ${backgroundHue.g}, ${backgroundHue.b})`,
          }}
        />
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(to right, #fff, transparent)',
          }}
        />
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(to bottom, transparent, #000)',
          }}
        />
      </div>
      <div
        className="absolute size-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white shadow-sm"
        style={{
          left: `${hsv?.s ?? 0}%`,
          top: `${100 - (hsv?.v ?? 0)}%`,
        }}
      />
    </div>
  );
}

ColorPickerArea.displayName = AREA_NAME;
