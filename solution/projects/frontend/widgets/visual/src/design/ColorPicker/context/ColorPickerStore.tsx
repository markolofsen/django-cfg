'use client';

import * as React from 'react';
import type { StoreState, Store, ColorValue, HSVColorValue, ColorFormat } from '../types';
import { rgbToHex, rgbToHsl, rgbToHsv, hsvToRgb as hsvToRgbFn } from '../lib/color-utils';

const StoreContext = React.createContext<Store | null>(null);

export function useStoreContext(consumerName: string) {
  const context = React.useContext(StoreContext);
  if (!context) {
    throw new Error(`\`${consumerName}\` must be used within ColorPicker`);
  }
  return context;
}

export function useStore<U>(selector: (state: StoreState) => U): U {
  const store = useStoreContext('useStore');

  const getSnapshot = React.useCallback(
    () => selector(store.getState()),
    [store, selector],
  );

  return React.useSyncExternalStore(store.subscribe, getSnapshot, getSnapshot);
}

function useLazyRef<T>(init: () => T): React.RefObject<T> {
  const ref = React.useRef<T | null>(null);
  if (ref.current === null) {
    ref.current = init();
  }
  return ref as React.RefObject<T>;
}

interface ColorPickerStoreProviderProps {
  children: React.ReactNode;
  initialColor: ColorValue;
  initialHsv: HSVColorValue;
  initialOpen: boolean;
  initialFormat: ColorFormat;
  onValueChange?: (value: string) => void;
  onOpenChange?: (open: boolean) => void;
  onFormatChange?: (format: ColorFormat) => void;
}

export function ColorPickerStoreProvider(props: ColorPickerStoreProviderProps) {
  const {
    children,
    initialColor,
    initialHsv,
    initialOpen,
    initialFormat,
    onValueChange,
    onOpenChange,
    onFormatChange,
  } = props;

  const listenersRef = useLazyRef(() => new Set<() => void>());
  const stateRef = useLazyRef<StoreState>(() => ({
    color: initialColor,
    hsv: initialHsv,
    open: initialOpen,
    format: initialFormat,
  }));

  const callbacksRef = React.useRef({ onValueChange, onOpenChange, onFormatChange });
  React.useEffect(() => {
    callbacksRef.current = { onValueChange, onOpenChange, onFormatChange };
  });

  const store = React.useMemo<Store>(() => {
    return {
      subscribe: (cb) => {
        listenersRef.current.add(cb);
        return () => listenersRef.current.delete(cb);
      },
      getState: () => stateRef.current,
      setColor: (value: ColorValue) => {
        if (Object.is(stateRef.current.color, value)) return;

        const prevState = { ...stateRef.current };
        stateRef.current.color = value;

        const cb = callbacksRef.current.onValueChange;
        if (cb) {
          const colorString = colorToString(value, prevState.format);
          cb(colorString);
        }

        store.notify();
      },
      setHsv: (value: HSVColorValue) => {
        if (Object.is(stateRef.current.hsv, value)) return;

        const prevState = { ...stateRef.current };
        stateRef.current.hsv = value;

        const cb = callbacksRef.current.onValueChange;
        if (cb) {
          const colorValue = hsvToRgb(value);
          const colorString = colorToString(colorValue, prevState.format);
          cb(colorString);
        }

        store.notify();
      },
      setOpen: (value: boolean) => {
        if (Object.is(stateRef.current.open, value)) return;

        stateRef.current.open = value;

        const cb = callbacksRef.current.onOpenChange;
        if (cb) cb(value);

        store.notify();
      },
      setFormat: (value: ColorFormat) => {
        if (Object.is(stateRef.current.format, value)) return;

        stateRef.current.format = value;

        const cb = callbacksRef.current.onFormatChange;
        if (cb) cb(value);

        store.notify();
      },
      notify: () => {
        for (const cb of listenersRef.current) {
          cb();
        }
      },
    };
  }, [listenersRef, stateRef]);

  return <StoreContext.Provider value={store}>{children}</StoreContext.Provider>;
}

function colorToString(color: ColorValue, format: ColorFormat): string {
  switch (format) {
    case 'hex':
      return rgbToHex(color);
    case 'rgb':
      return color.a < 1
        ? `rgba(${color.r}, ${color.g}, ${color.b}, ${color.a})`
        : `rgb(${color.r}, ${color.g}, ${color.b})`;
    case 'hsl': {
      const hsl = rgbToHsl(color);
      return color.a < 1
        ? `hsla(${hsl.h}, ${hsl.s}%, ${hsl.l}%, ${color.a})`
        : `hsl(${hsl.h}, ${hsl.s}%, ${hsl.l}%)`;
    }
    case 'hsb': {
      const hsv = rgbToHsv(color);
      return color.a < 1
        ? `hsba(${hsv.h}, ${hsv.s}%, ${hsv.v}%, ${color.a})`
        : `hsb(${hsv.h}, ${hsv.s}%, ${hsv.v}%)`;
    }
    default:
      return rgbToHex(color);
  }
}

function hsvToRgb(hsv: HSVColorValue): ColorValue {
  return hsvToRgbFn(hsv);
}
