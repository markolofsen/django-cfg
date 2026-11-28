'use client';

import * as React from 'react';
import { Slider } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { useColorPickerContext } from '../context/ColorPickerContext';
import { useStoreContext, useStore } from '../context/ColorPickerStore';
import { hsvToRgb } from '../lib/color-utils';
import type { HSVColorValue } from '../types';

const HUE_SLIDER_NAME = 'ColorPickerHueSlider';

export function ColorPickerHueSlider(props: React.ComponentProps<typeof Slider>) {
  const { className, ...sliderProps } = props;

  const context = useColorPickerContext(HUE_SLIDER_NAME);
  const store = useStoreContext(HUE_SLIDER_NAME);

  const hsv = useStore((state) => state.hsv);

  const onValueChange = React.useCallback(
    (values: number[]) => {
      const newHsv: HSVColorValue = {
        h: values[0] ?? 0,
        s: hsv?.s ?? 0,
        v: hsv?.v ?? 0,
        a: hsv?.a ?? 1,
      };
      store.setHsv(newHsv);
      store.setColor(hsvToRgb(newHsv));
    },
    [hsv, store],
  );

  return (
    <div
      className={cn(
        'relative flex w-full touch-none select-none items-center',
        className,
      )}
    >
      {/* Hue gradient background */}
      <div
        className="pointer-events-none absolute inset-x-0 h-3 rounded-full"
        style={{
          background:
            'linear-gradient(to right, #f00 0%, #ff0 17%, #0f0 33%, #0ff 50%, #00f 67%, #f0f 83%, #f00 100%)',
        }}
      />
      <Slider
        data-slot="color-picker-hue-slider"
        {...sliderProps}
        max={360}
        step={1}
        className="relative z-10 w-full"
        value={[hsv?.h ?? 0]}
        onValueChange={onValueChange}
        disabled={context.disabled}
      />
    </div>
  );
}

ColorPickerHueSlider.displayName = HUE_SLIDER_NAME;
