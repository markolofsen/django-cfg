'use client';

import { cva, type VariantProps } from 'class-variance-authority';
import * as React from 'react';
import { Input } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { useColorPickerContext } from '../context/ColorPickerContext';
import { useStoreContext, useStore } from '../context/ColorPickerStore';
import {
  rgbToHex,
  rgbToHsv,
  rgbToHsl,
  hslToRgb,
  hsvToRgb,
  parseColorString,
} from '../lib/color-utils';
import type { ColorValue, ColorPickerInputProps } from '../types';

const INPUT_NAME = 'ColorPickerInput';

const inputGroupItemVariants = cva(
  'h-8 [-moz-appearance:textfield] focus-visible:z-10 focus-visible:ring-1 [&::-webkit-inner-spin-button]:m-0 [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:m-0 [&::-webkit-outer-spin-button]:appearance-none',
  {
    variants: {
      position: {
        first: 'rounded-e-none',
        middle: '-ms-px rounded-none border-l-0',
        last: '-ms-px rounded-s-none border-l-0',
        isolated: '',
      },
    },
    defaultVariants: {
      position: 'isolated',
    },
  }
);

function InputGroupItem({
  className,
  position,
  ...props
}: React.ComponentProps<typeof Input> & VariantProps<typeof inputGroupItemVariants>) {
  return (
    <Input
      data-slot="color-picker-input"
      className={cn(inputGroupItemVariants({ position, className }))}
      {...props}
    />
  );
}

export function ColorPickerInput(props: ColorPickerInputProps) {
  const store = useStoreContext(INPUT_NAME);
  const context = useColorPickerContext(INPUT_NAME);

  const color = useStore((state) => state.color);
  const format = useStore((state) => state.format);
  const hsv = useStore((state) => state.hsv);

  const onColorChange = React.useCallback(
    (newColor: ColorValue) => {
      const newHsv = rgbToHsv(newColor);
      store.setColor(newColor);
      store.setHsv(newHsv);
    },
    [store],
  );

  if (format === 'hex') {
    return (
      <HexInput
        color={color}
        onColorChange={onColorChange}
        context={context}
        {...props}
      />
    );
  }

  if (format === 'rgb') {
    return (
      <RgbInput
        color={color}
        onColorChange={onColorChange}
        context={context}
        {...props}
      />
    );
  }

  if (format === 'hsl') {
    return (
      <HslInput
        color={color}
        onColorChange={onColorChange}
        context={context}
        {...props}
      />
    );
  }

  if (format === 'hsb') {
    return (
      <HsbInput
        hsv={hsv}
        onColorChange={onColorChange}
        context={context}
        {...props}
      />
    );
  }

  return null;
}

ColorPickerInput.displayName = INPUT_NAME;

interface FormatInputProps extends ColorPickerInputProps {
  color: ColorValue;
  onColorChange: (color: ColorValue) => void;
  context: ReturnType<typeof useColorPickerContext>;
}

function HexInput(props: FormatInputProps) {
  const {
    color,
    onColorChange,
    context,
    withoutAlpha,
    className,
    ...inputProps
  } = props;

  const hexValue = rgbToHex(color);
  const alphaValue = Math.round((color?.a ?? 1) * 100);

  const onHexChange = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      const parsedColor = parseColorString(value);
      if (parsedColor) {
        onColorChange({ ...parsedColor, a: color?.a ?? 1 });
      }
    },
    [color, onColorChange],
  );

  const onAlphaChange = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = Number.parseInt(event.target.value, 10);
      if (!Number.isNaN(value) && value >= 0 && value <= 100) {
        onColorChange({ ...color, a: value / 100 });
      }
    },
    [color, onColorChange],
  );

  if (withoutAlpha) {
    return (
      <InputGroupItem
        aria-label="Hex color value"
        position="isolated"
        {...inputProps}
        placeholder="#000000"
        className={cn('font-mono', className)}
        value={hexValue}
        onChange={onHexChange}
        disabled={context.disabled}
      />
    );
  }

  return (
    <div
      data-slot="color-picker-input-wrapper"
      className={cn('flex items-center', className)}
    >
      <InputGroupItem
        aria-label="Hex color value"
        position="first"
        {...inputProps}
        placeholder="#000000"
        className="flex-1 font-mono"
        value={hexValue}
        onChange={onHexChange}
        disabled={context.disabled}
      />
      <InputGroupItem
        aria-label="Alpha transparency percentage"
        position="last"
        {...inputProps}
        placeholder="100"
        inputMode="numeric"
        pattern="[0-9]*"
        min="0"
        max="100"
        className="w-14"
        value={alphaValue}
        onChange={onAlphaChange}
        disabled={context.disabled}
      />
    </div>
  );
}

function RgbInput(props: FormatInputProps) {
  const {
    color,
    onColorChange,
    context,
    withoutAlpha,
    className,
    ...inputProps
  } = props;

  const rValue = Math.round(color?.r ?? 0);
  const gValue = Math.round(color?.g ?? 0);
  const bValue = Math.round(color?.b ?? 0);
  const alphaValue = Math.round((color?.a ?? 1) * 100);

  const onChannelChange = React.useCallback(
    (channel: 'r' | 'g' | 'b' | 'a', max: number, isAlpha = false) =>
      (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = Number.parseInt(event.target.value, 10);
        if (!Number.isNaN(value) && value >= 0 && value <= max) {
          const newValue = isAlpha ? value / 100 : value;
          onColorChange({ ...color, [channel]: newValue });
        }
      },
    [color, onColorChange],
  );

  return (
    <div
      data-slot="color-picker-input-wrapper"
      className={cn('flex items-center', className)}
    >
      <InputGroupItem
        aria-label="Red color component (0-255)"
        position="first"
        {...inputProps}
        placeholder="0"
        inputMode="numeric"
        pattern="[0-9]*"
        min="0"
        max="255"
        className="w-14"
        value={rValue}
        onChange={onChannelChange('r', 255)}
        disabled={context.disabled}
      />
      <InputGroupItem
        aria-label="Green color component (0-255)"
        position="middle"
        {...inputProps}
        placeholder="0"
        inputMode="numeric"
        pattern="[0-9]*"
        min="0"
        max="255"
        className="w-14"
        value={gValue}
        onChange={onChannelChange('g', 255)}
        disabled={context.disabled}
      />
      <InputGroupItem
        aria-label="Blue color component (0-255)"
        position={withoutAlpha ? 'last' : 'middle'}
        {...inputProps}
        placeholder="0"
        inputMode="numeric"
        pattern="[0-9]*"
        min="0"
        max="255"
        className="w-14"
        value={bValue}
        onChange={onChannelChange('b', 255)}
        disabled={context.disabled}
      />
      {!withoutAlpha && (
        <InputGroupItem
          aria-label="Alpha transparency percentage"
          position="last"
          {...inputProps}
          placeholder="100"
          inputMode="numeric"
          pattern="[0-9]*"
          min="0"
          max="100"
          className="w-14"
          value={alphaValue}
          onChange={onChannelChange('a', 100, true)}
          disabled={context.disabled}
        />
      )}
    </div>
  );
}

function HslInput(props: FormatInputProps) {
  const {
    color,
    onColorChange,
    context,
    withoutAlpha,
    className,
    ...inputProps
  } = props;

  const hsl = React.useMemo(() => rgbToHsl(color), [color]);
  const alphaValue = Math.round((color?.a ?? 1) * 100);

  const onHslChannelChange = React.useCallback(
    (channel: 'h' | 's' | 'l', max: number) =>
      (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = Number.parseInt(event.target.value, 10);
        if (!Number.isNaN(value) && value >= 0 && value <= max) {
          const newHsl = { ...hsl, [channel]: value };
          const newColor = hslToRgb(newHsl, color?.a ?? 1);
          onColorChange(newColor);
        }
      },
    [hsl, color, onColorChange],
  );

  const onAlphaChange = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = Number.parseInt(event.target.value, 10);
      if (!Number.isNaN(value) && value >= 0 && value <= 100) {
        onColorChange({ ...color, a: value / 100 });
      }
    },
    [color, onColorChange],
  );

  return (
    <div
      data-slot="color-picker-input-wrapper"
      className={cn('flex items-center', className)}
    >
      <InputGroupItem
        aria-label="Hue degree (0-360)"
        position="first"
        {...inputProps}
        placeholder="0"
        inputMode="numeric"
        pattern="[0-9]*"
        min="0"
        max="360"
        className="w-14"
        value={hsl.h}
        onChange={onHslChannelChange('h', 360)}
        disabled={context.disabled}
      />
      <InputGroupItem
        aria-label="Saturation percentage (0-100)"
        position="middle"
        {...inputProps}
        placeholder="0"
        inputMode="numeric"
        pattern="[0-9]*"
        min="0"
        max="100"
        className="w-14"
        value={hsl.s}
        onChange={onHslChannelChange('s', 100)}
        disabled={context.disabled}
      />
      <InputGroupItem
        aria-label="Lightness percentage (0-100)"
        position={withoutAlpha ? 'last' : 'middle'}
        {...inputProps}
        placeholder="0"
        inputMode="numeric"
        pattern="[0-9]*"
        min="0"
        max="100"
        className="w-14"
        value={hsl.l}
        onChange={onHslChannelChange('l', 100)}
        disabled={context.disabled}
      />
      {!withoutAlpha && (
        <InputGroupItem
          aria-label="Alpha transparency percentage"
          position="last"
          {...inputProps}
          placeholder="100"
          inputMode="numeric"
          pattern="[0-9]*"
          min="0"
          max="100"
          className="w-14"
          value={alphaValue}
          onChange={onAlphaChange}
          disabled={context.disabled}
        />
      )}
    </div>
  );
}

interface HsbInputProps extends Omit<FormatInputProps, 'color'> {
  hsv: import('../types').HSVColorValue;
}

function HsbInput(props: HsbInputProps) {
  const {
    hsv,
    onColorChange,
    context,
    withoutAlpha,
    className,
    ...inputProps
  } = props;

  const alphaValue = Math.round((hsv?.a ?? 1) * 100);

  const onHsvChannelChange = React.useCallback(
    (channel: 'h' | 's' | 'v', max: number) =>
      (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = Number.parseInt(event.target.value, 10);
        if (!Number.isNaN(value) && value >= 0 && value <= max) {
          const newHsv = { ...hsv, [channel]: value };
          const newColor = hsvToRgb(newHsv);
          onColorChange(newColor);
        }
      },
    [hsv, onColorChange],
  );

  const onAlphaChange = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = Number.parseInt(event.target.value, 10);
      if (!Number.isNaN(value) && value >= 0 && value <= 100) {
        const currentColor = hsvToRgb(hsv);
        onColorChange({ ...currentColor, a: value / 100 });
      }
    },
    [hsv, onColorChange],
  );

  return (
    <div
      data-slot="color-picker-input-wrapper"
      className={cn('flex items-center', className)}
    >
      <InputGroupItem
        aria-label="Hue degree (0-360)"
        position="first"
        {...inputProps}
        placeholder="0"
        inputMode="numeric"
        pattern="[0-9]*"
        min="0"
        max="360"
        className="w-14"
        value={hsv?.h ?? 0}
        onChange={onHsvChannelChange('h', 360)}
        disabled={context.disabled}
      />
      <InputGroupItem
        aria-label="Saturation percentage (0-100)"
        position="middle"
        {...inputProps}
        placeholder="0"
        inputMode="numeric"
        pattern="[0-9]*"
        min="0"
        max="100"
        className="w-14"
        value={hsv?.s ?? 0}
        onChange={onHsvChannelChange('s', 100)}
        disabled={context.disabled}
      />
      <InputGroupItem
        aria-label="Brightness percentage (0-100)"
        position={withoutAlpha ? 'last' : 'middle'}
        {...inputProps}
        placeholder="0"
        inputMode="numeric"
        pattern="[0-9]*"
        min="0"
        max="100"
        className="w-14"
        value={hsv?.v ?? 0}
        onChange={onHsvChannelChange('v', 100)}
        disabled={context.disabled}
      />
      {!withoutAlpha && (
        <InputGroupItem
          aria-label="Alpha transparency percentage"
          position="last"
          {...inputProps}
          placeholder="100"
          inputMode="numeric"
          pattern="[0-9]*"
          min="0"
          max="100"
          className="w-14"
          value={alphaValue}
          onChange={onAlphaChange}
          disabled={context.disabled}
        />
      )}
    </div>
  );
}

