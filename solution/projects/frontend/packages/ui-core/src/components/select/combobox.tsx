"use client"

import { Check, ChevronsUpDown } from 'lucide-react';
import * as React from 'react';

import { useAppT } from '@djangocfg/i18n';
import { useStoredValue, type StorageType, type UseStoredValueOptions, useHighlight } from '../../hooks';
import { cn } from '../../lib/utils';
import { Badge } from '../data/badge';
import { Button } from '../forms/button';
import {
  Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList
} from '../navigation/command';
import { Popover, PopoverContent, PopoverTrigger } from '../overlay/popover';
import { SELECT_TRIGGER_CLASS } from './trigger';

export interface ComboboxOption {
  value: string
  label: string
  description?: string
  icon?: React.ComponentType<{ className?: string }>
  badge?: string | React.ReactNode
  disabled?: boolean
  style?: {
    badgeColor?: string
    iconColor?: string
    gradient?: string
  }
}

export interface ComboboxProps {
  options: ComboboxOption[]
  value?: string
  onValueChange?: (value: string) => void
  placeholder?: string
  searchPlaceholder?: string
  emptyText?: string
  className?: string
  disabled?: boolean
  renderOption?: (option: ComboboxOption) => React.ReactNode
  renderValue?: (option: ComboboxOption | undefined) => React.ReactNode
  /**
   * Replace the default `<Button variant="outline" w-full>` trigger
   * entirely. Use when the default trigger is too wide / too heavy for
   * the host (e.g. a 28×28 flag icon in a chat header). The element
   * receives Radix `PopoverTrigger asChild` props (refs + a11y) so
   * pass any native element here — `button`, `div role="button"`, etc.
   */
  renderTrigger?: (
    selected: ComboboxOption | undefined,
    open: boolean,
  ) => React.ReactElement
  /** Forwarded to `PopoverContent.className` — width, padding, etc. */
  contentClassName?: string
  /** Forwarded to `PopoverContent.style` — host can bump z-index when
   *  the combobox is rendered above another overlay (chat dock,
   *  modal, …) whose stacking context outranks ui-core's default. */
  contentStyle?: React.CSSProperties
  /** Custom filter function. If provided, replaces default filtering logic. */
  filterFunction?: (option: ComboboxOption, search: string) => boolean
  /**
   * When provided, the selected value is persisted under this key.
   *
   * On mount: if the stored value exists in the current options list,
   * it becomes the initial selection. If options are not yet loaded
   * (empty array), the component waits — it applies the stored value
   * once options become non-empty (see autoSelectFromOptions).
   *
   * @example storageKey="selected-queue"
   */
  storageKey?: string
  /** @default 'local' */
  storageType?: StorageType
  /** TTL in ms */
  storageTtl?: number
  /**
   * When true AND storageKey is set: after options load/change, if the
   * stored value is present in the new options list it is auto-selected
   * (calls onValueChange). If the stored value is no longer in the list
   * the selection is cleared to "".
   *
   * When false (default): stored value only seeds the initial value on
   * first render — subsequent option changes don't auto-correct the value.
   *
   * @default false
   */
  autoSelectFromOptions?: boolean
}

export function Combobox({
  options,
  value: controlledValue,
  onValueChange,
  placeholder,
  searchPlaceholder,
  emptyText,
  className,
  disabled = false,
  renderOption,
  renderValue,
  renderTrigger,
  contentClassName,
  contentStyle,
  filterFunction,
  storageKey,
  storageType,
  storageTtl,
  autoSelectFromOptions = false,
}: ComboboxProps) {
  const t = useAppT()
  const [open, setOpen] = React.useState(false)
  const [search, setSearch] = React.useState("")

  const storageOptions: UseStoredValueOptions | undefined =
    storageKey ? { storage: storageType ?? 'local', ttl: storageTtl } : undefined;

  const [storedValue, setStoredValue] = useStoredValue<string>(
    storageKey,
    controlledValue ?? '',
    storageOptions,
  );

  // Internal selection state — used only when parent doesn't control `value`.
  // Seeded from storedValue (which is initialValue / '' on SSR, real value post-hydration).
  const [internalValue, setInternalValue] = React.useState<string>(
    controlledValue !== undefined ? controlledValue : storedValue,
  );

  // The effective selected value: prefer controlled, fall back to internal
  const value = controlledValue !== undefined ? controlledValue : internalValue;

  const highlight = useHighlight(open, value)

  // autoSelectFromOptions: when options become available, validate stored value.
  // Runs whenever options change (async loads, filters, etc.)
  // Only acts when: storageKey is set, autoSelectFromOptions=true, options non-empty.
  // Guards:
  //   - don't override a value the user explicitly set to "" (intentional clear)
  //   - don't run while options are still loading (length === 0)
  const autoSelectApplied = React.useRef(false);

  React.useEffect(() => {
    if (!storageKey || !autoSelectFromOptions || options.length === 0) return;

    // Only auto-apply once per storageKey lifetime to avoid fighting user selections.
    // Reset when storageKey changes (handled by the key dependency below).
    if (autoSelectApplied.current) return;
    autoSelectApplied.current = true;

    const savedValue = storedValue;
    if (!savedValue) return; // nothing saved

    const existsInOptions = options.some((o) => o.value === savedValue && !o.disabled);

    if (existsInOptions) {
      // Restore saved selection
      if (controlledValue === undefined) {
        setInternalValue(savedValue);
      }
      onValueChange?.(savedValue);
    } else {
      // Saved value no longer valid — clear it
      setStoredValue('');
      if (controlledValue === undefined) {
        setInternalValue('');
      }
      onValueChange?.('');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [options, storageKey, autoSelectFromOptions]);

  // Reset autoSelectApplied when storageKey changes
  React.useEffect(() => {
    autoSelectApplied.current = false;
  }, [storageKey]);

  // Resolve translations
  const resolvedPlaceholder = placeholder ?? t('ui.select.placeholder')
  const resolvedSearchPlaceholder = searchPlaceholder ?? t('ui.select.search')
  const resolvedEmptyText = emptyText ?? t('ui.select.noResults')

  const selectedOption = React.useMemo(
    () => options.find((option) => option.value === value),
    [options, value]
  )

  const filteredOptions = React.useMemo(() => {
    if (!search) return options

    if (filterFunction) {
      return options.filter((option) => filterFunction(option, search))
    }

    const searchLower = search.toLowerCase()
    return options.filter(
      (option) =>
        option.label.toLowerCase().includes(searchLower) ||
        option.value.toLowerCase().includes(searchLower) ||
        option.description?.toLowerCase().includes(searchLower)
    )
  }, [options, search, filterFunction])

  const handleSelect = React.useCallback(
    (currentValue: string) => {
      const next = currentValue === value ? "" : currentValue;
      if (storageKey) setStoredValue(next);
      if (controlledValue === undefined) setInternalValue(next);
      onValueChange?.(next);
      setOpen(false);
    },
    [value, storageKey, setStoredValue, controlledValue, onValueChange],
  );

  // Render badge for selected option in trigger
  const renderSelectedBadge = (option: ComboboxOption) => {
    const { style, icon: Icon, badge } = option;
    const badgeStyle: React.CSSProperties = {};

    if (style?.gradient) {
      badgeStyle.background = style.gradient;
      badgeStyle.color = style.iconColor || "white";
    } else if (style?.badgeColor) {
      badgeStyle.backgroundColor = style.badgeColor;
      badgeStyle.color = style.iconColor || "white";
    }

    return (
      <div className="flex items-center gap-2">
        {Icon && <Icon className="h-4 w-4 shrink-0" />}
        <span className="truncate">{option.label}</span>
        {badge && (
          <Badge variant="secondary" className="text-xs" style={Object.keys(badgeStyle).length > 0 ? badgeStyle : undefined}>
            {badge}
          </Badge>
        )}
      </div>
    );
  };

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
        {renderTrigger ? (
          renderTrigger(selectedOption, open)
        ) : (
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className={cn(
              SELECT_TRIGGER_CLASS,
              !value && "text-muted-foreground",
              className
            )}
            disabled={disabled}
          >
            {renderValue && selectedOption
              ? renderValue(selectedOption)
              : selectedOption
              ? renderSelectedBadge(selectedOption)
              : resolvedPlaceholder}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        )}
      </PopoverTrigger>
      <PopoverContent
        className={cn("w-[var(--radix-popover-trigger-width)] p-0", contentClassName)}
        style={contentStyle}
        align="start"
      >
        {/* The highlight is controlled so it STARTS on the current selection —
            cmdk otherwise highlights the first item, and its open-time
            `scrollIntoView` then parks an 80-entry list at the top with the
            selected row far below the fold.
            `onValueChange` is mandatory here, not decorative: for a controlled
            `value` cmdk delegates every move to it and stores nothing itself,
            so without it the arrow keys would not move the highlight at all. */}
        <Command
          shouldFilter={false}
          value={highlight.value}
          onValueChange={highlight.setValue}
          className="flex flex-col"
        >
          <CommandInput
            placeholder={resolvedSearchPlaceholder}
            className="shrink-0"
            value={search}
            onValueChange={setSearch}
          />
          {/* CommandList is the scroller — see its own note. It caps itself to
              the popover's available height, so no wrapper is needed here and
              none may be added: one would take the scrolling away from cmdk. */}
          <CommandList ref={highlight.listRef}>
              {filteredOptions.length === 0 ? (
                <CommandEmpty>{resolvedEmptyText}</CommandEmpty>
              ) : (
                <CommandGroup>
                  {filteredOptions.map((option) => (
                  <CommandItem
                    key={option.value}
                    value={option.value}
                    onSelect={(currentValue) => {
                      if (!option.disabled) {
                        handleSelect(currentValue)
                      }
                    }}
                    disabled={option.disabled}
                  >
                    {option.icon && <option.icon className="mr-2 h-4 w-4 shrink-0" />}
                    {renderOption ? (
                      renderOption(option)
                    ) : (
                      <div className="flex flex-col flex-1 min-w-0">
                        <div className="flex items-center gap-2 truncate">
                          {/* `title` rather than wrapping: a row is a label to
                              scan, and a two-line one breaks both the vertical
                              rhythm and the constant step of the arrow keys. */}
                          <span className="truncate" title={option.label}>{option.label}</span>
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
                    {/* Trailing, and rendered ONLY when selected — an
                        always-present `opacity-0` placeholder indents every row
                        by 24px to reserve space for a mark at most one of them
                        ever shows. Absent, the label gets the full width;
                        present, `shrink-0` makes the label's truncation stop
                        exactly at the mark. */}
                    {value === option.value && (
                      <Check className="ml-2 h-4 w-4 shrink-0" />
                    )}
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
