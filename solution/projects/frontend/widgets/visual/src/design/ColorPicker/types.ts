import * as React from 'react';

export const colorFormats = ['hex', 'rgb', 'hsl', 'hsb'] as const;

export type ColorFormat = (typeof colorFormats)[number];

export interface ColorValue {
  r: number;
  g: number;
  b: number;
  a: number;
}

export interface HSVColorValue {
  h: number;
  s: number;
  v: number;
  a: number;
}

export interface StoreState {
  color: ColorValue;
  hsv: HSVColorValue;
  open: boolean;
  format: ColorFormat;
}

export interface Store {
  subscribe: (cb: () => void) => () => void;
  getState: () => StoreState;
  setColor: (value: ColorValue) => void;
  setHsv: (value: HSVColorValue) => void;
  setOpen: (value: boolean) => void;
  setFormat: (value: ColorFormat) => void;
  notify: () => void;
}

export interface ColorPickerContextValue {
  dir: 'ltr' | 'rtl';
  disabled?: boolean;
  inline?: boolean;
  readOnly?: boolean;
  required?: boolean;
}

export interface DivProps extends React.ComponentProps<'div'> {
  asChild?: boolean;
}

export interface ColorPickerProps
  extends Omit<DivProps, 'onValueChange'>,
    Pick<
      React.ComponentProps<typeof import('@djangocfg/ui-core/components').Popover>,
      'defaultOpen' | 'open' | 'onOpenChange' | 'modal'
    > {
  value?: string;
  defaultValue?: string;
  onValueChange?: (value: string) => void;
  dir?: 'ltr' | 'rtl';
  format?: ColorFormat;
  defaultFormat?: ColorFormat;
  onFormatChange?: (format: ColorFormat) => void;
  name?: string;
  asChild?: boolean;
  disabled?: boolean;
  inline?: boolean;
  readOnly?: boolean;
  required?: boolean;
}

export interface ColorPickerInputProps
  extends Omit<
    React.ComponentProps<typeof import('@djangocfg/ui-core/components').Input>,
    'value' | 'onChange' | 'color'
  > {
  withoutAlpha?: boolean;
}
