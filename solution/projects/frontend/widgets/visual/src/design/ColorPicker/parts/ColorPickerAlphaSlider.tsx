'use client';

import * as React from 'react';
import { Slider } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { useColorPickerContext } from '../context/ColorPickerContext';
import { useStoreContext, useStore } from '../context/ColorPickerStore';

const ALPHA_SLIDER_NAME = 'ColorPickerAlphaSlider';

export function ColorPickerAlphaSlider(props: React.ComponentProps<typeof Slider>) {
  const { className, ...sliderProps } = props;

  const context = useColorPickerContext(ALPHA_SLIDER_NAME);
  const store = useStoreContext(ALPHA_SLIDER_NAME);

  const color = useStore((state) => state.color);
  const hsv = useStore((state) => state.hsv);

  const onValueChange = React.useCallback(
    (values: number[]) => {
      const alpha = (values[0] ?? 0) / 100;
      const newColor = { ...color, a: alpha };
      const newHsv = { ...hsv, a: alpha };
      store.setColor(newColor);
      store.setHsv(newHsv);
    },
    [color, hsv, store],
  );

  const opaqueColor = `rgb(${color?.r ?? 0}, ${color?.g ?? 0}, ${color?.b ?? 0})`;
  const transparentColor = `rgba(${color?.r ?? 0}, ${color?.g ?? 0}, ${color?.b ?? 0}, 0)`;

  return (
    <div
      className={cn(
        'relative flex w-full touch-none select-none items-center',
        className,
      )}
    >
      {/* Checkerboard background */}
      <div
        className="pointer-events-none absolute inset-x-0 h-3 rounded-full"
        style={{
          background:
            'linear-gradient(45deg, #ccc 25%, transparent 25%), linear-gradient(-45deg, #ccc 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #ccc 75%), linear-gradient(-45deg, transparent 75%, #ccc 75%)',
          backgroundSize: '8px 8px',
          backgroundPosition: '0 0, 0 4px, 4px -4px, -4px 0px',
        }}
      />
      {/* Alpha gradient overlay */}
      <div
        className="pointer-events-none absolute inset-x-0 h-3 rounded-full"
        style={{
          background: `linear-gradient(to right, ${transparentColor}, ${opaqueColor})`,
        }}
      />
      <Slider
        data-slot="color-picker-alpha-slider"
        {...sliderProps}
        max={100}
        step={1}
        disabled={context.disabled}
        className="relative z-10 w-full"
        value={[Math.round((color?.a ?? 1) * 100)]}
        onValueChange={onValueChange}
      />
    </div>
  );
}

ColorPickerAlphaSlider.displayName = ALPHA_SLIDER_NAME;
