"use client"

import * as React from 'react';

import { CheckIcon, ChevronDownIcon, ChevronUpIcon } from '@radix-ui/react-icons';
import * as SelectPrimitive from '@radix-ui/react-select';

import { cn } from '../../lib/utils';
import { Badge } from '../data/badge';
import { CONTROL_SIZE, type FieldControlSize } from '../forms/control-size';

/**
 * Radix `<Select.Item value="" />` is reserved (it's how Radix represents
 * "cleared selection"), so passing an empty string at the consumer level
 * throws. This wrapper transparently substitutes empty strings with a
 * sentinel for the Radix layer and unwraps it again on `onValueChange`,
 * letting consumers use `''` for "none" without inventing their own marker.
 *
 * Applies to `Select` (controlled value/defaultValue/onValueChange) and
 * `SelectItem` (item value).
 */
const EMPTY_SENTINEL = '__empty__';
const toRadix = (raw: string | undefined): string | undefined => {
  if (raw === undefined) return undefined;
  return raw === '' ? EMPTY_SENTINEL : raw;
};
const fromRadix = (raw: string): string => (raw === EMPTY_SENTINEL ? '' : raw);

function Select(
  props: React.ComponentPropsWithoutRef<typeof SelectPrimitive.Root>,
): React.ReactElement {
  const { value, defaultValue, onValueChange, ...rest } = props;
  const handleChange = React.useCallback(
    (next: string) => {
      onValueChange?.(fromRadix(next));
    },
    [onValueChange],
  );
  return (
    <SelectPrimitive.Root
      value={toRadix(value)}
      defaultValue={toRadix(defaultValue)}
      onValueChange={onValueChange ? handleChange : undefined}
      {...rest}
    />
  );
}

const SelectGroup = SelectPrimitive.Group

const SelectValue = SelectPrimitive.Value

const SelectTrigger = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger> & {
    icon?: React.ComponentType<{ className?: string }>;
    /**
     * `ghost` strips the bordered field chrome (border, bg, shadow, fixed
     * height) for use as a flat inline control — e.g. a compact dropdown in a
     * status bar or toolbar where the trigger should read like a plain button.
     */
    variant?: "default" | "ghost";
    /**
     * Height from the shared control ladder (`forms/control-size.ts`): the same
     * name as a `Button` or `Input` gives the same height. Ignored by `ghost`,
     * which has no fixed height.
     */
    size?: FieldControlSize;
  }
>(({ className, children, icon: Icon, variant = "default", size = "default", ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={cn(
      "flex items-center justify-between whitespace-nowrap ring-offset-background data-[placeholder]:text-muted-foreground focus:outline-none disabled:cursor-not-allowed disabled:opacity-50",
      // Same type size as `Input`: 16px on a phone (no iOS zoom, same line as the field beside it), 14px from `md`.
      variant === "default" ? "text-base md:text-sm" : "text-sm",
      variant === "default" &&
        cn(
          CONTROL_SIZE[size].height,
          "w-full rounded-[var(--radius)] border border-border bg-transparent px-3 shadow-sm focus:ring-1 focus:ring-ring",
        ),
      variant === "ghost" &&
        "rounded-md px-2 py-0.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground data-[state=open]:bg-muted data-[state=open]:text-foreground",
      className
    )}
    {...props}
  >
    {/*
     * Outer wrapper is a flex row so a leading `icon` (any size) stays
     * vertically centered with the value text. `line-clamp-1` is applied
     * to the value child, NOT this wrapper — putting it here would set
     * `display:-webkit-box` and silently kill the flex centering.
     */}
    <span className="flex items-center gap-2 flex-1 min-w-0 [&>span]:line-clamp-1">
      {Icon && (
        <span className="flex shrink-0 items-center justify-center">
          <Icon className="h-4 w-4" />
        </span>
      )}
      {children}
    </span>
    <SelectPrimitive.Icon asChild>
      <ChevronDownIcon className="h-4 w-4 opacity-50" />
    </SelectPrimitive.Icon>
  </SelectPrimitive.Trigger>
))
SelectTrigger.displayName = SelectPrimitive.Trigger.displayName

const SelectScrollUpButton = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.ScrollUpButton>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.ScrollUpButton>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.ScrollUpButton
    ref={ref}
    className={cn(
      "flex cursor-default items-center justify-center py-1",
      className
    )}
    {...props}
  >
    <ChevronUpIcon className="h-4 w-4" />
  </SelectPrimitive.ScrollUpButton>
))
SelectScrollUpButton.displayName = SelectPrimitive.ScrollUpButton.displayName

const SelectScrollDownButton = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.ScrollDownButton>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.ScrollDownButton>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.ScrollDownButton
    ref={ref}
    className={cn(
      "flex cursor-default items-center justify-center py-1",
      className
    )}
    {...props}
  >
    <ChevronDownIcon className="h-4 w-4" />
  </SelectPrimitive.ScrollDownButton>
))
SelectScrollDownButton.displayName =
  SelectPrimitive.ScrollDownButton.displayName

const SelectContent = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Content>
>(({ className, children, position = "popper", ...props }, ref) => (
  <SelectPrimitive.Portal>
    <SelectPrimitive.Content
      ref={ref}
      className={cn(
        "relative z-[1400] max-h-(--radix-select-content-available-height) min-w-32 overflow-y-auto overflow-x-hidden rounded-[var(--radius-popover)] border bg-popover backdrop-blur-xl text-popover-foreground shadow-(--popup-shadow) data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        position === "popper" &&
          "data-[side=bottom]:translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1 data-[side=top]:-translate-y-1",
        className
      )}
      position={position}
      {...props}
    >
      <SelectScrollUpButton />
      <SelectPrimitive.Viewport
        className={cn(
          "p-(--menu-padding)",
          position === "popper" &&
            "h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]"
        )}
      >
        {children}
      </SelectPrimitive.Viewport>
      <SelectScrollDownButton />
    </SelectPrimitive.Content>
  </SelectPrimitive.Portal>
))
SelectContent.displayName = SelectPrimitive.Content.displayName

const SelectLabel = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Label>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Label>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Label
    ref={ref}
    className={cn("px-(--menu-item-px) py-(--menu-item-py) text-(length:--menu-label-font-size) font-(weight:--menu-label-weight) text-(color:--menu-label-color)", className)}
    {...props}
  />
))
SelectLabel.displayName = SelectPrimitive.Label.displayName

const SelectItem = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item> & {
    key?: React.Key;
    icon?: React.ComponentType<{ className?: string }>;
    badge?: string | React.ReactNode;
    /**
     * Optional secondary line shown under the label in the dropdown.
     * Rendered OUTSIDE `SelectPrimitive.ItemText`, so it does NOT
     * appear in the trigger — only `children` (the label) does. Use
     * this for two-line options whose trigger must stay single-line.
     */
    description?: React.ReactNode;
  }
>(({ className, children, icon: Icon, badge, description, value, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    value={value === '' ? EMPTY_SENTINEL : value}
    className={cn(
      "relative flex w-full cursor-default select-none items-center rounded-[var(--radius-sm)] py-(--menu-item-py) pl-2 pr-8 text-(length:--menu-font-size) outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
      className
    )}
    {...props}
  >
    <span className="absolute right-2 flex h-3.5 w-3.5 items-center justify-center">
      <SelectPrimitive.ItemIndicator>
        <CheckIcon className="h-4 w-4" />
      </SelectPrimitive.ItemIndicator>
    </span>
    <div className="flex items-center gap-2 flex-1 min-w-0 pr-6">
      {Icon && <Icon className="h-4 w-4 shrink-0" />}
      <div className="flex min-w-0 flex-1 flex-col">
        <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
        {description && (
          <span className="text-xs text-muted-foreground">{description}</span>
        )}
      </div>
      {badge && (
        <Badge variant="outline" className="text-xs shrink-0">
          {badge}
        </Badge>
      )}
    </div>
  </SelectPrimitive.Item>
))
SelectItem.displayName = SelectPrimitive.Item.displayName

const SelectSeparator = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Separator>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Separator> & { key?: React.Key }
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Separator
    ref={ref}
    className={cn("-mx-1 my-1 h-px bg-muted", className)}
    {...props}
  />
))
SelectSeparator.displayName = SelectPrimitive.Separator.displayName

export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton,
}
