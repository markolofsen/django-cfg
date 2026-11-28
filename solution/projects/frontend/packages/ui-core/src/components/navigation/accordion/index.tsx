"use client"

import * as React from 'react';

import * as AccordionPrimitive from '@radix-ui/react-accordion';
import { ChevronDownIcon } from '@radix-ui/react-icons';

import { useStoredValue, type StorageType, type UseStoredValueOptions } from '../../../hooks';
import { cn } from '../../../lib/utils';

type AccordionSingleProps = React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Root> & {
  type: 'single'
  storageKey?: string
  storageType?: StorageType
  storageTtl?: number
}

type AccordionMultipleProps = React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Root> & {
  type: 'multiple'
  storageKey?: string
  storageType?: StorageType
  storageTtl?: number
}

export type AccordionProps = AccordionSingleProps | AccordionMultipleProps

const Accordion = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitive.Root>,
  AccordionProps
>(({ storageKey, storageType, storageTtl, ...props }, ref) => {
  const storageOptions: UseStoredValueOptions | undefined =
    storageKey ? { storage: storageType ?? 'local', ttl: storageTtl } : undefined;

  const isSingle = props.type === 'single';

  // For single: persist string; for multiple: persist string[]
  const initialSingle = (props as AccordionSingleProps).defaultValue ?? ((props as AccordionSingleProps).value as string | undefined) ?? '';
  const initialMultiple = (props as AccordionMultipleProps).defaultValue ?? ((props as AccordionMultipleProps).value as string[] | undefined) ?? [];

  const [storedSingle, setStoredSingle] = useStoredValue<string>(
    isSingle ? storageKey : undefined,
    initialSingle,
    storageOptions,
  );
  const [storedMultiple, setStoredMultiple] = useStoredValue<string[]>(
    !isSingle ? storageKey : undefined,
    initialMultiple,
    storageOptions,
  );

  if (isSingle) {
    // Drop ``type`` from ``rest`` — we re-apply it below as a literal so
    // the Radix discriminated-union narrows correctly; leaving it in
    // ``rest`` makes TS flag a duplicate (TS2783).
    const { onValueChange, value, defaultValue, type: _t, ...rest } = props as AccordionSingleProps & { onValueChange?: (v: string) => void };
    void _t;
    const handleValueChange = storageKey
      ? (newValue: string) => { setStoredSingle(newValue); onValueChange?.(newValue); }
      : onValueChange;
    const extraProps = storageKey && value === undefined && storedSingle
      ? { defaultValue: storedSingle }
      : defaultValue !== undefined ? { defaultValue } : {};

    return (
      <AccordionPrimitive.Root
        ref={ref}
        type="single"
        value={value}
        onValueChange={handleValueChange}
        {...extraProps}
        {...rest}
      />
    );
  }

  const { onValueChange, value, defaultValue, type: _t, ...rest } = props as AccordionMultipleProps & { onValueChange?: (v: string[]) => void };
  void _t;
  const handleValueChange = storageKey
    ? (newValue: string[]) => { setStoredMultiple(newValue); onValueChange?.(newValue); }
    : onValueChange;
  const extraProps = storageKey && value === undefined && storedMultiple.length > 0
    ? { defaultValue: storedMultiple }
    : defaultValue !== undefined ? { defaultValue } : {};

  return (
    <AccordionPrimitive.Root
      ref={ref}
      type="multiple"
      value={value}
      onValueChange={handleValueChange}
      {...extraProps}
      {...rest}
    />
  );
})
Accordion.displayName = "Accordion"

const AccordionItem = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Item> & { key?: React.Key }
>(({ className, ...props }, ref) => (
  <AccordionPrimitive.Item
    ref={ref}
    className={cn("border-b", className)}
    {...props}
  />
))
AccordionItem.displayName = "AccordionItem"

const AccordionTrigger = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Trigger>
>(({ className, children, ...props }, ref) => (
  <AccordionPrimitive.Header className="flex">
    <AccordionPrimitive.Trigger
      ref={ref}
      className={cn(
        "flex flex-1 items-center justify-between py-4 text-sm font-medium transition-all hover:underline text-left [&[data-state=open]>svg]:rotate-180",
        className
      )}
      {...props}
    >
      {children}
      <ChevronDownIcon className="h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200" />
    </AccordionPrimitive.Trigger>
  </AccordionPrimitive.Header>
))
AccordionTrigger.displayName = AccordionPrimitive.Trigger.displayName

const AccordionContent = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <AccordionPrimitive.Content
    ref={ref}
    className="overflow-hidden text-sm data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down"
    {...props}
  >
    <div className={cn("pb-4 pt-0", className)}>{children}</div>
  </AccordionPrimitive.Content>
))
AccordionContent.displayName = AccordionPrimitive.Content.displayName

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent }
