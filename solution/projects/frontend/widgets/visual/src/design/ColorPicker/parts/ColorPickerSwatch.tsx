'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { useColorPickerContext } from '../context/ColorPickerContext';
import { useStore } from '../context/ColorPickerStore';
import { colorToString } from '../lib/color-utils';

const SWATCH_NAME = 'ColorPickerSwatch';

export function ColorPickerSwatch(props: React.ComponentProps<'div'> & { asChild?: boolean }) {
  const { className, ...swatchProps } = props;

  const context = useColorPickerContext(SWATCH_NAME);

  const color = useStore((state) => state.color);
  const format = useStore((state) => state.format);

  const backgroundStyle = React.useMemo(() => {
    if (!color) {
      return {
        background:
          'linear-gradient(to bottom right, transparent calc(50% - 1px), hsl(var(--destructive)) calc(50% - 1px) calc(50% + 1px), transparent calc(50% + 1px)) no-repeat',
      };
    }

    const colorString = `rgba(${color.r}, ${color.g}, ${color.b}, ${color.a})`;

    if (color.a < 1) {
      return {
        background: `linear-gradient(${colorString}, ${colorString}), repeating-conic-gradient(#ccc 0% 25%, #fff 0% 50%) 0% 50% / 8px 8px`,
      };
    }

    return {
      backgroundColor: colorString,
    };
  }, [color]);

  const ariaLabel = !color
    ? 'No color selected'
    : `Current color: ${colorToString(color, format)}`;

  return (
    <div
      role="img"
      aria-label={ariaLabel}
      data-slot="color-picker-swatch"
      {...swatchProps}
      className={cn(
        'box-border size-8 rounded-sm border shadow-sm',
        context.disabled && 'opacity-50',
        className,
      )}
      style={{
        ...backgroundStyle,
        forcedColorAdjust: 'none',
      }}
    />
  );
}

ColorPickerSwatch.displayName = SWATCH_NAME;
