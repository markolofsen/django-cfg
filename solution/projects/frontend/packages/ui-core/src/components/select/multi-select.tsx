"use client"

import { Check, ChevronsUpDown, X } from 'lucide-react';
import * as React from 'react';

import { useAppT } from '@djangocfg/i18n';
import { useStoredValue, type StorageType, type UseStoredValueOptions } from '../../hooks';
import { cn } from '../../lib/utils';
import { Badge } from '../data/badge';
import { Button } from '../forms/button';
import {
    Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList
} from '../navigation/command';
import { Popover, PopoverContent, PopoverTrigger } from '../overlay/popover';
import { SELECT_TRIGGER_MULTI_CLASS } from './trigger';

export interface MultiSelectOption {
  value: string
  label: string
  description?: string
  disabled?: boolean
}

export interface MultiSelectProps {
  options: MultiSelectOption[]
  value?: string[]
  onChange?: (value: string[]) => void
  placeholder?: string
  searchPlaceholder?: string
  emptyText?: string
  className?: string
  disabled?: boolean
  maxDisplay?: number
  /**
   * When provided, the selected values array is persisted under this key.
   *
   * On mount: stored values that are present in the current options are
   * restored. Values that no longer exist in options are silently dropped
   * (safe against stale data from removed options).
   *
   * @example storageKey="selected-tags"
   */
  storageKey?: string
  /** @default 'local' */
  storageType?: StorageType
  /** TTL in ms */
  storageTtl?: number
  /**
   * When true AND storageKey is set: after options load/change, the stored
   * selection is filtered to only include values present in the current
   * options. Values not in options are removed from the selection and
   * from storage.
   *
   * When false (default): stored values are only used to seed the initial
   * selection. Subsequent option changes don't re-filter.
   *
   * @default false
   */
  autoSelectFromOptions?: boolean
}

const EMPTY_ARRAY: string[] = [];

export function MultiSelect({
  options,
  value: controlledValue,
  onChange,
  placeholder,
  searchPlaceholder,
  emptyText,
  className,
  disabled = false,
  maxDisplay = 3,
  storageKey,
  storageType,
  storageTtl,
  autoSelectFromOptions = false,
}: MultiSelectProps) {
  const t = useAppT()
  const [open, setOpen] = React.useState(false)
  const [search, setSearch] = React.useState("")

  const storageOptions: UseStoredValueOptions | undefined =
    storageKey ? { storage: storageType ?? 'local', ttl: storageTtl } : undefined;

  const [storedValue, setStoredValue] = useStoredValue<string[]>(
    storageKey,
    controlledValue ?? EMPTY_ARRAY,
    storageOptions,
  );

  // Internal selection state for uncontrolled mode
  const [internalValue, setInternalValue] = React.useState<string[]>(
    controlledValue !== undefined ? controlledValue : storedValue,
  );

  const value = controlledValue !== undefined ? controlledValue : internalValue;

  // Resolve translations
  const resolvedPlaceholder = placeholder ?? t('ui.select.placeholder')
  const resolvedSearchPlaceholder = searchPlaceholder ?? t('ui.select.search')
  const resolvedEmptyText = emptyText ?? t('ui.select.noResults')

  // autoSelectFromOptions: filter stored selection to valid options only
  const autoSelectApplied = React.useRef(false);

  React.useEffect(() => {
    if (!storageKey || !autoSelectFromOptions || options.length === 0) return;
    if (autoSelectApplied.current) return;
    autoSelectApplied.current = true;

    const saved = storedValue;
    if (!saved || saved.length === 0) return;

    const validOptionValues = new Set(
      options.filter((o) => !o.disabled).map((o) => o.value)
    );
    const filtered = saved.filter((v) => validOptionValues.has(v));

    // Only update if something actually changed
    const changed = filtered.length !== saved.length ||
      filtered.some((v, i) => v !== saved[i]);

    if (changed) {
      setStoredValue(filtered);
      if (controlledValue === undefined) setInternalValue(filtered);
      onChange?.(filtered);
    } else if (filtered.length > 0) {
      // Restore valid selection to parent
      if (controlledValue === undefined) setInternalValue(filtered);
      onChange?.(filtered);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [options, storageKey, autoSelectFromOptions]);

  React.useEffect(() => {
    autoSelectApplied.current = false;
  }, [storageKey]);

  const selectedOptions = React.useMemo(
    () => options.filter((option) => value.includes(option.value)),
    [options, value]
  )

  const filteredOptions = React.useMemo(() => {
    if (!search) return options
    const searchLower = search.toLowerCase()
    return options.filter(
      (option) =>
        option.label.toLowerCase().includes(searchLower) ||
        option.value.toLowerCase().includes(searchLower) ||
        option.description?.toLowerCase().includes(searchLower)
    )
  }, [options, search])

  const handleSelect = React.useCallback((optionValue: string) => {
    const newValue = value.includes(optionValue)
      ? value.filter((v) => v !== optionValue)
      : [...value, optionValue];
    if (storageKey) setStoredValue(newValue);
    if (controlledValue === undefined) setInternalValue(newValue);
    onChange?.(newValue);
  }, [value, storageKey, setStoredValue, controlledValue, onChange]);

  const handleRemove = React.useCallback((optionValue: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const newValue = value.filter((v) => v !== optionValue);
    if (storageKey) setStoredValue(newValue);
    if (controlledValue === undefined) setInternalValue(newValue);
    onChange?.(newValue);
  }, [value, storageKey, setStoredValue, controlledValue, onChange]);

  const displayValue = React.useMemo(() => {
    if (selectedOptions.length === 0) {
      return <span className="text-muted-foreground">{resolvedPlaceholder}</span>
    }

    const displayed = selectedOptions.slice(0, maxDisplay)
    const remaining = selectedOptions.length - maxDisplay

    return (
      <div className="flex flex-wrap gap-1">
        {displayed.map((option) => (
          <Badge
            key={option.value}
            variant="secondary"
            className="mr-1 text-xs"
          >
            {option.label}
            <button
              className="ml-1 rounded-full hover:bg-muted-foreground/20"
              onClick={(e) => handleRemove(option.value, e)}
              disabled={disabled}
              aria-label={t('ui.actions.remove', { item: option.label })}
            >
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}
        {remaining > 0 && (
          <Badge variant="outline" className="text-xs">
            {t('ui.select.moreItems', { count: remaining })}
          </Badge>
        )}
      </div>
    )
  }, [selectedOptions, maxDisplay, resolvedPlaceholder, disabled, t, handleRemove])

  return (
    <Popover
      open={open}
      onOpenChange={(isOpen) => {
        setOpen(isOpen)
        if (!isOpen) {
          setSearch("")
        }
      }}
    >
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            SELECT_TRIGGER_MULTI_CLASS,
            className
          )}
          disabled={disabled}
        >
          <div className="flex-1 text-left overflow-hidden">
            {displayValue}
          </div>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0" align="start">
        <Command shouldFilter={false} className="flex flex-col">
          <CommandInput
            placeholder={resolvedSearchPlaceholder}
            className="shrink-0"
            value={search}
            onValueChange={setSearch}
          />
          {/* CommandList is the scroller (it caps itself to the popover's
              available height) — never wrap it in a scrolling div, which hands
              the scrolling to a container cmdk cannot see.
              The min-height keeps the panel from collapsing to a sliver while a
              narrow search still matches one row. */}
          <CommandList className="min-h-[100px]">
              {filteredOptions.length === 0 ? (
                <CommandEmpty>{resolvedEmptyText}</CommandEmpty>
              ) : (
                <CommandGroup>
                  {filteredOptions.map((option) => {
                    const isSelected = value.includes(option.value)
                    return (
                      <CommandItem
                        key={option.value}
                        value={option.value}
                        onSelect={() => {
                          if (!option.disabled) {
                            handleSelect(option.value)
                          }
                        }}
                        disabled={option.disabled}
                      >
                        <Check
                          className={cn(
                            "mr-2 h-4 w-4 shrink-0",
                            isSelected ? "opacity-100" : "opacity-0"
                          )}
                        />
                        <div className="flex flex-col flex-1 min-w-0">
                          <span className="truncate">{option.label}</span>
                          {option.description && (
                            <span className="text-xs text-muted-foreground truncate">
                              {option.description}
                            </span>
                          )}
                        </div>
                      </CommandItem>
                    )
                  })}
                </CommandGroup>
              )}
            </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
