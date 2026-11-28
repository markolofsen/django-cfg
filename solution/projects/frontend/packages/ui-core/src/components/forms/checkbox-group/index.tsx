"use client"

import * as React from "react"

import { cn } from "../../../lib/utils"
import { Checkbox } from "../checkbox"

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

interface CheckboxGroupContextValue {
  value: string[]
  toggle: (value: string) => void
  disabled: boolean
  name?: string
  /** Ties `CheckboxGroupLabel` to the group's `aria-labelledby`. */
  labelId: string
  /** Ties every item's `aria-describedby` to the group's description. */
  descriptionId: string
}

const CheckboxGroupContext = React.createContext<CheckboxGroupContextValue | null>(null)

function useCheckboxGroupContext(consumerName: string) {
  const context = React.useContext(CheckboxGroupContext)
  if (!context) {
    throw new Error(`\`${consumerName}\` must be used within \`CheckboxGroup\``)
  }
  return context
}

// ─────────────────────────────────────────────────────────────────────────────
// CheckboxGroup Root
// ─────────────────────────────────────────────────────────────────────────────

interface CheckboxGroupProps extends React.ComponentProps<"div"> {
  value?: string[]
  defaultValue?: string[]
  onValueChange?: (value: string[]) => void
  disabled?: boolean
  name?: string
}

function CheckboxGroup({
  className,
  value: valueProp,
  defaultValue,
  onValueChange,
  disabled = false,
  name,
  "aria-labelledby": ariaLabelledBy,
  ...props
}: CheckboxGroupProps) {
  const isControlled = valueProp !== undefined
  const [uncontrolledValue, setUncontrolledValue] = React.useState<string[]>(defaultValue ?? [])

  const value = isControlled ? valueProp : uncontrolledValue

  // Ids for the label and description, so the group announces as one thing
  // rather than as a run of unrelated checkboxes.
  const id = React.useId()
  const labelId = `${id}-label`
  const descriptionId = `${id}-description`

  // The membership rule lives here, not on the item: an item that computed the
  // next array from a captured `value` toggled against a stale snapshot when
  // two arrived in one tick.
  const toggle = React.useCallback(
    (member: string) => {
      const from = isControlled ? valueProp : undefined
      const next = (current: string[]) =>
        current.includes(member)
          ? current.filter((entry) => entry !== member)
          : [...current, member]

      if (isControlled) {
        onValueChange?.(next(from ?? []))
        return
      }
      setUncontrolledValue((current) => {
        const value = next(current)
        onValueChange?.(value)
        return value
      })
    },
    [isControlled, valueProp, onValueChange],
  )

  const contextValue = React.useMemo<CheckboxGroupContextValue>(
    () => ({ value, toggle, disabled, name, labelId, descriptionId }),
    [value, toggle, disabled, name, labelId, descriptionId],
  )

  return (
    <CheckboxGroupContext.Provider value={contextValue}>
      {/* `role="group"`: without it a screen reader reads the items as
          unrelated checkboxes and never says what they have in common.
          `CheckboxGroupLabel` names it; a caller passing its own
          `aria-labelledby` wins. */}
      <div
        role="group"
        aria-labelledby={ariaLabelledBy ?? labelId}
        data-slot="checkbox-group"
        data-disabled={disabled ? "" : undefined}
        className={cn("peer flex flex-col gap-2", className)}
        {...props}
      />
    </CheckboxGroupContext.Provider>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// CheckboxGroupLabel
// ─────────────────────────────────────────────────────────────────────────────

function CheckboxGroupLabel({ className, id, ...props }: React.ComponentProps<"div">) {
  const context = useCheckboxGroupContext("CheckboxGroupLabel")
  return (
    <div
      id={id ?? context.labelId}
      data-slot="checkbox-group-label"
      className={cn(
        "text-foreground/70 text-sm leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
        className,
      )}
      {...props}
    />
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// CheckboxGroupList
// ─────────────────────────────────────────────────────────────────────────────

interface CheckboxGroupListProps extends React.ComponentProps<"div"> {
  orientation?: "horizontal" | "vertical"
}

function CheckboxGroupList({
  className,
  orientation = "vertical",
  ...props
}: CheckboxGroupListProps) {
  return (
    // Optional: the root already stacks its children, so this exists for the
    // horizontal case and for separating the items from a label and a
    // description that share the root. Same `gap-2` either way — one spacing
    // for one component.
    <div
      data-slot="checkbox-group-list"
      data-orientation={orientation}
      className={cn(
        "flex gap-2",
        orientation === "horizontal" ? "flex-row flex-wrap items-center" : "flex-col",
        className,
      )}
      {...props}
    />
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// CheckboxGroupItem
// ─────────────────────────────────────────────────────────────────────────────

interface CheckboxGroupItemProps
  extends Omit<React.ComponentProps<typeof Checkbox>, "value" | "checked" | "onCheckedChange"> {
  value: string
  disabled?: boolean
  /** Classes for the ROW. The box itself takes `checkboxClassName`. */
  className?: string
  checkboxClassName?: string
}

function CheckboxGroupItem({
  className,
  checkboxClassName,
  children,
  value,
  disabled: disabledProp,
  ...props
}: CheckboxGroupItemProps) {
  const context = useCheckboxGroupContext("CheckboxGroupItem")
  const isDisabled = disabledProp || context.disabled
  const isChecked = context.value.includes(value)

  return (
    // The whole row is the target, not just the box: a 16px hit area for a
    // choice the row already names is the commonest reason a list like this
    // feels unresponsive. `w-full`, so the row spans its list.
    <label
      data-slot="checkbox-group-row"
      data-state={isChecked ? "checked" : "unchecked"}
      data-disabled={isDisabled ? "" : undefined}
      className={cn(
        "flex w-full select-none items-center gap-2 text-sm leading-none",
        isDisabled ? "cursor-not-allowed opacity-50" : "cursor-pointer",
        className,
      )}
    >
      {/* The shared `Checkbox`, not a second implementation of one. The
          hand-rolled button here carried its own border, size and tick, so a
          form holding both drew two different checkboxes. */}
      <Checkbox
        data-slot="checkbox-group-item"
        aria-describedby={context.descriptionId}
        {...props}
        checked={isChecked}
        onCheckedChange={() => context.toggle(value)}
        disabled={isDisabled}
        className={checkboxClassName}
      />
      {/* Submitted with the form. `name` was accepted and then dropped, so a
          native submit sent nothing for a group the caller had named. */}
      {context.name && isChecked ? (
        <input type="hidden" name={context.name} value={value} />
      ) : null}
      {children}
    </label>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// CheckboxGroupDescription
// ─────────────────────────────────────────────────────────────────────────────

function CheckboxGroupDescription({ className, id, ...props }: React.ComponentProps<"div">) {
  const context = useCheckboxGroupContext("CheckboxGroupDescription")
  return (
    <div
      id={id ?? context.descriptionId}
      data-slot="checkbox-group-description"
      className={cn(
        "text-[0.8rem] text-muted-foreground leading-none",
        className,
      )}
      {...props}
    />
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// CheckboxGroupMessage
// ─────────────────────────────────────────────────────────────────────────────

function CheckboxGroupMessage({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="checkbox-group-message"
      className={cn(
        "text-[0.8rem] text-muted-foreground leading-none",
        className,
      )}
      {...props}
    />
  )
}

export {
  CheckboxGroup,
  CheckboxGroupDescription,
  CheckboxGroupItem,
  CheckboxGroupLabel,
  CheckboxGroupList,
  CheckboxGroupMessage,
}
export type { CheckboxGroupProps, CheckboxGroupItemProps, CheckboxGroupListProps }
