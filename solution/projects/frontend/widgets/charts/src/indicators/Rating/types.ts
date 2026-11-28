import * as React from 'react';

export type Direction = 'ltr' | 'rtl';
export type Orientation = 'horizontal' | 'vertical';
export type ActivationMode = 'automatic' | 'manual';
export type Size = 'default' | 'sm' | 'lg';
export type Step = 0.5 | 1;
export type DataState = 'full' | 'partial' | 'empty';
export type FocusIntent = 'first' | 'last' | 'prev' | 'next';

export interface StoreState {
  value: number;
  hoveredValue: number | null;
}

export interface Store {
  subscribe: (callback: () => void) => () => void;
  getState: () => StoreState;
  setState: <K extends keyof StoreState>(key: K, value: StoreState[K]) => void;
  notify: () => void;
}

export interface ItemData {
  id: string;
  ref: React.RefObject<HTMLButtonElement | null>;
  value: number;
  disabled: boolean;
}

export interface RatingContextValue {
  rootId: string;
  dir: Direction;
  orientation: Orientation;
  activationMode: ActivationMode;
  size: Size;
  max: number;
  step: Step;
  clearable: boolean;
  disabled: boolean;
  readOnly: boolean;
  getAutoIndex: (instanceId: string) => number;
}

export interface FocusContextValue {
  tabStopId: string | null;
  onItemFocus: (tabStopId: string) => void;
  onItemShiftTab: () => void;
  onFocusableItemAdd: () => void;
  onFocusableItemRemove: () => void;
  onItemRegister: (item: ItemData) => void;
  onItemUnregister: (id: string) => void;
  getItems: () => ItemData[];
}

export interface RatingProps extends React.ComponentProps<'div'> {
  value?: number;
  defaultValue?: number;
  onValueChange?: (value: number) => void;
  onHover?: (value: number | null) => void;
  max?: number;
  activationMode?: ActivationMode;
  dir?: Direction;
  orientation?: Orientation;
  size?: Size;
  asChild?: boolean;
  step?: Step;
  clearable?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  required?: boolean;
  name?: string;
}

export interface RatingItemProps
  extends Omit<React.ComponentProps<'button'>, 'children'> {
  index?: number;
  asChild?: boolean;
  children?: React.ReactNode | ((dataState: DataState) => React.ReactNode);
}
