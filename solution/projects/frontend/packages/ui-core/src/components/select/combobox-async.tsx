"use client"

import { Check, ChevronsUpDown, Loader2, X } from 'lucide-react';
import * as React from 'react';

import { useAppT } from '@djangocfg/i18n';
import { cn } from '../../lib/utils';
import { Badge } from '../data/badge';
import { Button } from '../forms/button';
import {
  Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList
} from '../navigation/command';
import { Popover, PopoverContent, PopoverTrigger } from '../overlay/popover';
import { SELECT_TRIGGER_CLASS } from './trigger';
import { useHighlight } from '../../hooks';

export interface ComboboxAsyncOption {
  value: string
  label: string
  description?: string
  icon?: React.ComponentType<{ className?: string }>
  badge?: string | React.ReactNode
  disabled?: boolean
}

export interface ComboboxAsyncProps {
  /**
   * Options currently visible in the dropdown.
   *
   * The parent owns this list — typically a memoised projection of the
   * latest server response keyed off ``searchValue``. The component does
   * NOT filter ``options`` further; whatever you pass in is what shows.
   */
  options: ComboboxAsyncOption[]

  /**
   * Selected option id, or ``null`` when nothing is selected.
   * Always controlled — there's no internal state, because the canonical
   * value lives upstream (a form, a parent context, query string, …).
   */
  value: string | null

  /** Fires with ``null`` when the user clears the selection. */
  onValueChange: (value: string | null) => void

  /**
   * Controlled search input. Parent debounces and feeds it back into the
   * data hook that produces ``options`` — same shape as
   * ``MultiSelectProAsync``.
   */
  searchValue: string
  onSearchChange: (value: string) => void

  /** Show a spinner row + "Searching…" affordance while the parent fetch is in flight. */
  isLoading?: boolean

  /**
   * Labels for ids that are selected but might not be present in
   * ``options`` right now (e.g. dialog opened with a pre-filled value
   * whose row isn't in the latest search response).
   *
   * Without this the trigger would show the raw id. Provide one entry per
   * id you'd like resolved; the component falls back to the id only if
   * neither ``options`` nor ``seedOptions`` contain it.
   */
  seedOptions?: ComboboxAsyncOption[]

  placeholder?: string
  searchPlaceholder?: string
  emptyText?: string
  loadingText?: string
  className?: string
  disabled?: boolean
  /** Whether to render an inline ``×`` button on the trigger to clear. */
  clearable?: boolean

  renderOption?: (option: ComboboxAsyncOption) => React.ReactNode
  renderValue?: (option: ComboboxAsyncOption | undefined) => React.ReactNode
}

/**
 * Single-select combobox with parent-owned async search.
 *
 * Pairs with ``MultiSelectProAsync`` — same controlled-search /
 * isLoading / seedOptions contract, just for "pick one" cases. Use
 * this when the dataset is too large to ship to the browser up-front
 * (typeaheads against a server-side search endpoint).
 *
 * For static / pre-loaded option lists use the plain ``Combobox`` —
 * its built-in client-side filtering is the right tool there.
 */
export function ComboboxAsync({
  options,
  value,
  onValueChange,
  searchValue,
  onSearchChange,
  isLoading = false,
  seedOptions,
  placeholder,
  searchPlaceholder,
  emptyText,
  loadingText,
  className,
  disabled = false,
  clearable = true,
  renderOption,
  renderValue,
}: ComboboxAsyncProps) {
  const t = useAppT()
  const [open, setOpen] = React.useState(false)
  const highlight = useHighlight(open, value)

  const resolvedPlaceholder = placeholder ?? t('ui.select.placeholder')
  const resolvedSearchPlaceholder = searchPlaceholder ?? t('ui.select.search')
  const resolvedEmptyText = emptyText ?? t('ui.select.noResults')
  const resolvedLoadingText = loadingText ?? t('ui.select.loading')

  // Resolve the selected option from options first (freshest label),
  // fall back to seedOptions for the case where the value's row isn't
  // in the current search response.
  const selectedOption = React.useMemo<ComboboxAsyncOption | undefined>(() => {
    if (!value) return undefined
    return (
      options.find((o) => o.value === value) ??
      seedOptions?.find((o) => o.value === value)
    )
  }, [options, seedOptions, value])

  const handleSelect = React.useCallback(
    (currentValue: string) => {
      // Click again on the selected row → clear.
      const next = currentValue === value ? null : currentValue
      onValueChange(next)
      setOpen(false)
    },
    [value, onValueChange],
  )

  const handleClear = React.useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault()
      e.stopPropagation()
      onValueChange(null)
    },
    [onValueChange],
  )

  return (
    <Popover
      open={open}
      onOpenChange={(isOpen) => {
        setOpen(isOpen)
        if (!isOpen) onSearchChange('')
      }}
    >
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            SELECT_TRIGGER_CLASS,
            !selectedOption && "text-muted-foreground",
            className
          )}
          disabled={disabled}
        >
          {renderValue && selectedOption
            ? renderValue(selectedOption)
            : selectedOption
            ? <SelectedTriggerLabel option={selectedOption} />
            : <span className="truncate">{resolvedPlaceholder}</span>}
          <div className="ml-2 flex shrink-0 items-center gap-1">
            {clearable && selectedOption && !disabled ? (
              <span
                role="button"
                tabIndex={-1}
                aria-label="Clear selection"
                onClick={handleClear}
                onMouseDown={(e) => e.stopPropagation()}
                className="rounded-sm p-0.5 opacity-50 transition-opacity hover:opacity-100"
              >
                <X className="h-4 w-4" />
              </span>
            ) : null}
            <ChevronsUpDown className="h-4 w-4 opacity-50" />
          </div>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0" align="start">
        {/* Controlled so the highlight starts on the current selection rather
            than the first row. `onValueChange` is mandatory with a controlled
            `value`: cmdk then stores nothing itself and delegates every move to
            it, so without it the arrow keys would not move the highlight. */}
        <Command
          shouldFilter={false}
          value={highlight.value}
          onValueChange={highlight.setValue}
          className="flex flex-col"
        >
          <CommandInput
            placeholder={resolvedSearchPlaceholder}
            className="shrink-0"
            value={searchValue}
            onValueChange={onSearchChange}
          />
          {/* CommandList is the scroller (it caps itself to the popover's
              available height) — do not wrap it in a scrolling div: that hands
              the scrolling to a container cmdk cannot see. */}
          <CommandList ref={highlight.listRef}>
              {isLoading && options.length === 0 ? (
                <div className="flex items-center gap-2 px-3 py-6 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>{resolvedLoadingText}</span>
                </div>
              ) : options.length === 0 ? (
                <CommandEmpty>{resolvedEmptyText}</CommandEmpty>
              ) : (
                <CommandGroup>
                  {options.map((option) => (
                    <CommandItem
                      key={option.value}
                      value={option.value}
                      onSelect={(currentValue) => {
                        if (!option.disabled) handleSelect(currentValue)
                      }}
                      disabled={option.disabled}
                    >
                      {option.icon && <option.icon className="mr-2 h-4 w-4 shrink-0" />}
                      {renderOption ? (
                        renderOption(option)
                      ) : (
                        <div className="flex flex-col flex-1 min-w-0">
                          <div className="flex items-center gap-2 truncate">
                            <span className="truncate">{option.label}</span>
                            {option.badge && (
                              <Badge variant="outline" className="text-xs shrink-0">
                                {option.badge}
                              </Badge>
                            )}
                          </div>
                          {option.description && (
                            <span className="text-xs text-muted-foreground truncate">
                              {option.description}
                            </span>
                          )}
                        </div>
                      )}
                    
                      {/* Trailing and only when selected: an always-rendered
                          `opacity-0` mark indents every row to hold space one
                          row at most ever uses. Absent it, the label gets the
                          full width; present, `shrink-0` stops the label's
                          truncation exactly at the mark. */}
                      {value === option.value && <Check className="ml-2 h-4 w-4 shrink-0" />}
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

function SelectedTriggerLabel({ option }: { option: ComboboxAsyncOption }) {
  const Icon = option.icon
  return (
    <div className="flex min-w-0 items-center gap-2">
      {Icon && <Icon className="h-4 w-4 shrink-0" />}
      <span className="truncate">{option.label}</span>
      {option.badge && (
        <Badge variant="secondary" className="shrink-0 text-xs">
          {option.badge}
        </Badge>
      )}
    </div>
  )
}
