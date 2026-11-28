'use client';

import { Slot as SlotPrimitive } from '@radix-ui/react-slot';
import { useDirection as useDirectionPrimitive } from '@radix-ui/react-direction';
import * as React from 'react';
import { useComposedRefs } from '@djangocfg/ui-core/lib';
import { cn } from '@djangocfg/ui-core/lib';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@djangocfg/ui-core/components';
import { VisuallyHiddenInput } from '@djangocfg/ui-core/components';
import { Button } from '@djangocfg/ui-core/components';
import { ColorPickerStoreProvider, useStoreContext, useStore } from './context/ColorPickerStore';
import { ColorPickerProvider, useColorPickerContext } from './context/ColorPickerContext';
import { hexToRgb, rgbToHsv, rgbToHex } from './lib/color-utils';
import type { ColorPickerProps } from './types';

const ROOT_NAME = 'ColorPicker';
const TRIGGER_NAME = 'ColorPickerTrigger';
const CONTENT_NAME = 'ColorPickerContent';

export function ColorPicker(props: ColorPickerProps) {
  const {
    value: valueProp,
    defaultValue = '#000000',
    onValueChange,
    format: formatProp,
    defaultFormat = 'hex',
    onFormatChange,
    defaultOpen,
    open: openProp,
    onOpenChange,
    name,
    disabled,
    inline,
    readOnly,
    required,
    ...rootProps
  } = props;

  const colorString = valueProp ?? defaultValue;
  const color = hexToRgb(colorString);

  // Mount-time seed for the store, deliberately frozen. These feed the
  // provider's `initial*` props, which it reads once; recomputing them on a
  // prop change would suggest a later `value` re-seeds the picker, and it does
  // not — the store owns the colour after mount.
  const initialState = React.useMemo(() => ({
    color,
    hsv: rgbToHsv(color),
    open: openProp ?? defaultOpen ?? false,
    format: formatProp ?? defaultFormat,
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }), []);

  return (
    <ColorPickerStoreProvider
      initialColor={initialState.color}
      initialHsv={initialState.hsv}
      initialOpen={initialState.open}
      initialFormat={initialState.format}
      onValueChange={onValueChange}
      onOpenChange={onOpenChange}
      onFormatChange={onFormatChange}
    >
      <ColorPickerImpl
        {...rootProps}
        value={valueProp}
        defaultOpen={defaultOpen}
        open={openProp}
        name={name}
        disabled={disabled}
        inline={inline}
        readOnly={readOnly}
        required={required}
      />
    </ColorPickerStoreProvider>
  );
}

ColorPicker.displayName = ROOT_NAME;

type ColorPickerImplProps = Omit<
  ColorPickerProps,
  | 'defaultValue'
  | 'onValueChange'
  | 'onOpenChange'
  | 'format'
  | 'defaultFormat'
  | 'onFormatChange'
>;

function ColorPickerImpl(props: ColorPickerImplProps) {
  const {
    value: valueProp,
    dir: dirProp,
    defaultOpen,
    open: openProp,
    name,
    ref,
    asChild,
    disabled,
    inline,
    modal,
    readOnly,
    required,
    ...rootProps
  } = props;

  const store = useStoreContext('ColorPickerImpl');

  const dir = useDirectionPrimitive(dirProp);

  const [formTrigger, setFormTrigger] = React.useState<HTMLDivElement | null>(null);
  const composedRef = useComposedRefs(ref, (node: HTMLDivElement | null) => setFormTrigger(node));
  const isFormControl = formTrigger ? !!formTrigger.closest('form') : true;

  React.useLayoutEffect(() => {
    if (valueProp !== undefined) {
      const currentState = store.getState();
      const color = hexToRgb(valueProp, currentState.color.a);
      const hsv = rgbToHsv(color);
      store.setColor(color);
      store.setHsv(hsv);
    }
  }, [valueProp, store]);

  React.useLayoutEffect(() => {
    if (openProp !== undefined) {
      store.setOpen(openProp);
    }
  }, [openProp, store]);

  const contextValue = React.useMemo(() => ({
    dir,
    disabled,
    inline,
    readOnly,
    required,
  }), [dir, disabled, inline, readOnly, required]);

  const value = useStore((state) => rgbToHex(state.color));
  const open = useStore((state) => state.open);

  const RootPrimitive = asChild ? SlotPrimitive : 'div';

  if (inline) {
    return (
      <ColorPickerProvider value={contextValue}>
        <RootPrimitive {...rootProps} ref={composedRef} />
        {isFormControl && (
          <VisuallyHiddenInput
            type="hidden"
            control={formTrigger}
            name={name}
            value={value}
            disabled={disabled}
            readOnly={readOnly}
            required={required}
          />
        )}
      </ColorPickerProvider>
    );
  }

  return (
    <ColorPickerProvider value={contextValue}>
      <Popover
        defaultOpen={defaultOpen}
        open={open}
        onOpenChange={store.setOpen}
        modal={modal}
      >
        <RootPrimitive {...rootProps} ref={composedRef} />
        {isFormControl && (
          <VisuallyHiddenInput
            type="hidden"
            control={formTrigger}
            name={name}
            value={value}
            disabled={disabled}
            readOnly={readOnly}
            required={required}
          />
        )}
      </Popover>
    </ColorPickerProvider>
  );
}

ColorPickerImpl.displayName = 'ColorPickerImpl';

export function ColorPickerTrigger(props: React.ComponentProps<typeof PopoverTrigger> & { asChild?: boolean }) {
  const { asChild, disabled, ...triggerProps } = props;

  const context = useColorPickerContext(TRIGGER_NAME);

  const isDisabled = disabled || context.disabled;

  const TriggerPrimitive = asChild ? SlotPrimitive : Button;

  if (context.inline) {
    return (
      <TriggerPrimitive
        data-slot="color-picker-trigger"
        disabled={isDisabled}
        {...triggerProps}
      />
    );
  }

  return (
    <PopoverTrigger asChild disabled={isDisabled}>
      <TriggerPrimitive data-slot="color-picker-trigger" {...triggerProps} />
    </PopoverTrigger>
  );
}

ColorPickerTrigger.displayName = TRIGGER_NAME;

export function ColorPickerContent(props: React.ComponentProps<typeof PopoverContent> & { asChild?: boolean }) {
  const { asChild, className, children, ...popoverContentProps } = props;

  const context = useColorPickerContext(CONTENT_NAME);

  if (context.inline) {
    const ContentPrimitive = asChild ? SlotPrimitive : 'div';

    return (
      <ContentPrimitive
        data-slot="color-picker-content"
        {...popoverContentProps}
        className={cn('flex w-[340px] flex-col gap-4 p-4', className)}
      >
        {children}
      </ContentPrimitive>
    );
  }

  return (
    <PopoverContent
      data-slot="color-picker-content"
      asChild={asChild}
      {...popoverContentProps}
      className={cn('flex w-[340px] flex-col gap-4 p-4', className)}
    >
      {children}
    </PopoverContent>
  );
}

ColorPickerContent.displayName = CONTENT_NAME;
