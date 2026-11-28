'use client';

import { PipetteIcon } from 'lucide-react';
import * as React from 'react';
import { Button } from '@djangocfg/ui-core/components';
import { useColorPickerContext } from '../context/ColorPickerContext';
import { useStoreContext, useStore } from '../context/ColorPickerStore';
import { hexToRgb, rgbToHsv } from '../lib/color-utils';

const EYE_DROPPER_NAME = 'ColorPickerEyeDropper';

interface EyeDropper {
  open: (options?: { signal?: AbortSignal }) => Promise<{ sRGBHex: string }>;
}

declare global {
  interface Window {
    EyeDropper?: {
      new (): EyeDropper;
    };
  }
}

export function ColorPickerEyeDropper(props: React.ComponentProps<typeof Button>) {
  const { size: sizeProp, children, disabled, ...buttonProps } = props;

  const context = useColorPickerContext(EYE_DROPPER_NAME);
  const store = useStoreContext(EYE_DROPPER_NAME);

  const color = useStore((state) => state.color);

  const isDisabled = disabled || context.disabled;

  const onEyeDropper = React.useCallback(async () => {
    if (!window.EyeDropper) return;

    try {
      const eyeDropper = new window.EyeDropper();
      const result = await eyeDropper.open();

      if (result.sRGBHex) {
        const currentAlpha = color?.a ?? 1;
        const newColor = hexToRgb(result.sRGBHex, currentAlpha);
        const newHsv = rgbToHsv(newColor);
        store.setColor(newColor);
        store.setHsv(newHsv);
      }
    } catch (error) {
      console.warn('EyeDropper error:', error);
    }
  }, [color, store]);

  const hasEyeDropper = typeof window !== 'undefined' && !!window.EyeDropper;

  if (!hasEyeDropper) return null;

  const size = sizeProp ?? (children ? 'default' : 'icon');

  return (
    <Button
      data-slot="color-picker-eye-dropper"
      {...buttonProps}
      variant="outline"
      size={size}
      onClick={onEyeDropper}
      disabled={isDisabled}
    >
      {children ?? <PipetteIcon />}
    </Button>
  );
}

ColorPickerEyeDropper.displayName = EYE_DROPPER_NAME;
