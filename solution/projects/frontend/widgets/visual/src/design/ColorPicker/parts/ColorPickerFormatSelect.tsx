'use client';

import * as React from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { useColorPickerContext } from '../context/ColorPickerContext';
import { useStoreContext, useStore } from '../context/ColorPickerStore';
import { colorFormats } from '../types';
import type { ColorFormat } from '../types';

const FORMAT_SELECT_NAME = 'ColorPickerFormatSelect';

export function ColorPickerFormatSelect(
  props: Omit<React.ComponentProps<typeof Select>, 'value' | 'onValueChange'> & {
    className?: string;
  }
) {
  const { disabled, className, ...selectProps } = props;

  const context = useColorPickerContext(FORMAT_SELECT_NAME);
  const store = useStoreContext(FORMAT_SELECT_NAME);
  const isDisabled = disabled || context.disabled;

  const format = useStore((state) => state.format);

  const onFormatChange = React.useCallback(
    (value: string) => {
      store.setFormat(value as ColorFormat);
    },
    [store],
  );

  return (
    <Select
      data-slot="color-picker-format-select"
      {...selectProps}
      value={format}
      onValueChange={onFormatChange}
      disabled={isDisabled}
    >
      <SelectTrigger
        data-slot="color-picker-format-select-trigger"
        className={cn('h-8 text-xs', className)}
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {colorFormats.map((format) => (
          <SelectItem key={format} value={format}>
            {format.toUpperCase()}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

ColorPickerFormatSelect.displayName = FORMAT_SELECT_NAME;
