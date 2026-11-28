"use client"

import { Check, ChevronsUpDown, Search, X } from 'lucide-react';
import * as React from 'react';
import { countries, type TCountryCode } from 'countries-list';

import { cn } from '../../lib/utils';
import { Badge } from '../data/badge';
import { Button } from '../forms/button';
import { Checkbox } from '../forms/checkbox';
import {
  Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList
} from '../navigation/command';
import { Input } from '../forms/input';
import { Popover, PopoverContent, PopoverTrigger } from '../overlay/popover';
import { ScrollArea } from '../layout/scroll-area';
import { Flag } from '../specialized/flag';
import { SELECT_TRIGGER_MULTI_CLASS } from './trigger';
import { useHighlight } from '../../hooks';

export interface CountryOption {
  code: TCountryCode;
  name: string;
  native: string;
}

export type CountrySelectVariant = 'dropdown' | 'inline';

export interface CountrySelectProps {
  /** Selected country codes (ISO 3166-1 alpha-2) */
  value?: string[];
  /** Callback when selection changes */
  onChange?: (value: string[]) => void;
  /** Allow multiple selection */
  multiple?: boolean;
  /** Display variant: dropdown (popover) or inline (scrollable list) */
  variant?: CountrySelectVariant;
  /** Placeholder text (default: "Select country...") */
  placeholder?: string;
  /** Search placeholder text (default: "Search...") */
  searchPlaceholder?: string;
  /** Empty results text (default: "No countries found") */
  emptyText?: string;
  /** Additional CSS class */
  className?: string;
  /** Disable the component */
  disabled?: boolean;
  /** Max badges to display (for multiple dropdown mode) */
  maxDisplay?: number;
  /** Custom country name resolver (for i18n) */
  getCountryName?: (code: TCountryCode) => string;
  /** Show native name alongside translated name */
  showNativeName?: boolean;
  /** Filter to specific country codes */
  allowedCountries?: TCountryCode[];
  /** Exclude specific country codes */
  excludedCountries?: TCountryCode[];
  /** Max height for inline variant */
  maxHeight?: number;
  /** Show search input */
  showSearch?: boolean;
  /** Custom label for selected count (receives count as param). Example: (count) => `${count} selected` */
  selectedCountLabel?: (count: number) => string;
  /** Custom label for "more items" badge (receives count as param). Example: (count) => `+${count} more` */
  moreItemsLabel?: (count: number) => string;
}

/**
 * Country Select component with SVG flags
 *
 * Supports:
 * - Single and multiple selection
 * - Dropdown (popover) and inline (scrollable list) variants
 * - Custom country name translations via getCountryName prop
 * - Country filtering via allowedCountries/excludedCountries
 *
 * Uses ISO 3166-1 alpha-2 country codes.
 *
 * @example Single dropdown
 * ```tsx
 * <CountrySelect
 *   value={country ? [country] : []}
 *   onChange={(codes) => setCountry(codes[0])}
 * />
 * ```
 *
 * @example Multiple dropdown
 * ```tsx
 * <CountrySelect
 *   multiple
 *   value={countries}
 *   onChange={setCountries}
 * />
 * ```
 *
 * @example Inline list with checkboxes
 * ```tsx
 * <CountrySelect
 *   variant="inline"
 *   multiple
 *   value={countries}
 *   onChange={setCountries}
 *   maxHeight={300}
 * />
 * ```
 *
 * @example With i18n translations
 * ```tsx
 * <CountrySelect
 *   value={value}
 *   onChange={onChange}
 *   getCountryName={(code) => i18nCountries.getName(code, locale)}
 * />
 * ```
 */
export function CountrySelect({
  value = [],
  onChange,
  multiple = false,
  variant = 'dropdown',
  placeholder,
  searchPlaceholder,
  emptyText,
  className,
  disabled = false,
  maxDisplay = 3,
  getCountryName,
  showNativeName = false,
  allowedCountries,
  excludedCountries,
  maxHeight = 300,
  showSearch = true,
  selectedCountLabel = (count: number) => `${count} selected`,
  moreItemsLabel = (count: number) => `+${count} more`,
}: CountrySelectProps) {
  const [open, setOpen] = React.useState(false)
  const highlight = useHighlight(open, value[0])
  const [search, setSearch] = React.useState("")

  // Resolve defaults
  const resolvedPlaceholder = placeholder ?? 'Select country...'
  const resolvedSearchPlaceholder = searchPlaceholder ?? 'Search...'
  const resolvedEmptyText = emptyText ?? 'No countries found'

  // Build country options
  const allCountries = React.useMemo<CountryOption[]>(() => {
    let codes = Object.keys(countries) as TCountryCode[];

    // Apply filters
    if (allowedCountries?.length) {
      codes = codes.filter(code => allowedCountries.includes(code));
    }
    if (excludedCountries?.length) {
      codes = codes.filter(code => !excludedCountries.includes(code));
    }

    return codes
      .map((code) => ({
        code,
        name: getCountryName?.(code) ?? countries[code].name,
        native: countries[code].native,
      }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [getCountryName, allowedCountries, excludedCountries]);

  const selectedCountries = React.useMemo(
    () => allCountries.filter((c) => value.includes(c.code)),
    [allCountries, value]
  )

  const filteredCountries = React.useMemo(() => {
    if (!search) return allCountries
    const searchLower = search.toLowerCase()
    return allCountries.filter(
      (c) =>
        c.name.toLowerCase().includes(searchLower) ||
        c.native.toLowerCase().includes(searchLower) ||
        c.code.toLowerCase().includes(searchLower)
    )
  }, [allCountries, search])

  const handleSelect = React.useCallback((code: string) => {
    if (multiple) {
      const newValue = value.includes(code)
        ? value.filter((v) => v !== code)
        : [...value, code]
      onChange?.(newValue)
    } else {
      onChange?.([code])
      if (variant === 'dropdown') {
        setOpen(false)
      }
    }
  }, [multiple, value, onChange, variant])

  const handleRemove = React.useCallback((code: string, e: React.MouseEvent) => {
    e.stopPropagation()
    onChange?.(value.filter((v) => v !== code))
  }, [value, onChange])

  // Used only by the dropdown variant below, but MUST be declared before the
  // `inline` early return — a hook after a conditional return changes the hook
  // count when `variant` differs between renders and crashes React (#310).
  const displayValue = React.useMemo(() => {
    if (selectedCountries.length === 0) {
      return <span className="text-muted-foreground">{resolvedPlaceholder}</span>
    }

    if (!multiple && selectedCountries.length === 1) {
      const country = selectedCountries[0]!;
      return (
        <div className="flex items-center gap-2">
          <Flag countryCode={country.code} rounded className="h-3 w-4 shrink-0" />
          <span>{country.name}</span>
        </div>
      );
    }

    const displayed = selectedCountries.slice(0, maxDisplay)
    const remaining = selectedCountries.length - maxDisplay

    return (
      <div className="flex flex-wrap gap-1">
        {displayed.map((country) => (
          <Badge
            key={country.code}
            variant="secondary"
            className="mr-1 text-xs"
          >
            <Flag countryCode={country.code} rounded className="mr-1 h-3 w-4 shrink-0" />
            {country.name}
            <button
              className="ml-1 rounded-full hover:bg-muted-foreground/20"
              onClick={(e) => handleRemove(country.code, e)}
              disabled={disabled}
              aria-label={`Remove ${country.name}`}
            >
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}
        {remaining > 0 && (
          <Badge variant="outline" className="text-xs">
            {moreItemsLabel(remaining)}
          </Badge>
        )}
      </div>
    )
  }, [selectedCountries, maxDisplay, resolvedPlaceholder, disabled, multiple, handleRemove, moreItemsLabel])

  // Inline variant
  if (variant === 'inline') {
    return (
      <div className={cn("space-y-3", className)}>
        {/* Search input */}
        {showSearch && (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder={resolvedSearchPlaceholder}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
              disabled={disabled}
            />
          </div>
        )}

        {/* Selected count */}
        {multiple && selectedCountries.length > 0 && (
          <p className="text-sm text-muted-foreground">
            {selectedCountLabel(selectedCountries.length)}
          </p>
        )}

        {/* Country list */}
        <ScrollArea style={{ height: maxHeight }} className="rounded-[var(--radius-popover)] border">
          <div className="p-1">
            {filteredCountries.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                {resolvedEmptyText}
              </p>
            ) : (
              filteredCountries.map((country) => {
                const isSelected = value.includes(country.code);
                return (
                  <label
                    key={country.code}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 rounded-[var(--radius-sm)] cursor-pointer',
                      'hover:bg-accent/50 transition-colors',
                      isSelected && 'bg-primary/5',
                      disabled && 'opacity-50 cursor-not-allowed',
                    )}
                  >
                    {multiple ? (
                      <Checkbox
                        checked={isSelected}
                        onCheckedChange={() => !disabled && handleSelect(country.code)}
                        disabled={disabled}
                      />
                    ) : (
                      <div className={cn(
                        "h-4 w-4 rounded-full border-2 flex items-center justify-center",
                        isSelected ? "border-primary bg-primary" : "border-muted-foreground"
                      )}>
                        {isSelected && <div className="h-2 w-2 rounded-full bg-primary-foreground" />}
                      </div>
                    )}
                    <Flag countryCode={country.code} rounded className="h-4 w-6 shrink-0" />
                    <div className="flex flex-col flex-1 min-w-0">
                      <span className={cn('text-sm', isSelected && 'font-medium')}>
                        {country.name}
                      </span>
                      {showNativeName && country.native !== country.name && (
                        <span className="text-xs text-muted-foreground">
                          {country.native}
                        </span>
                      )}
                    </div>
                  </label>
                );
              })
            )}
          </div>
        </ScrollArea>
      </div>
    );
  }

  // Dropdown variant (displayValue is memoized above, before the inline guard)
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
        {/* Controlled highlight. `onValueChange` is mandatory alongside it:
            with a controlled `value` cmdk stores nothing itself and delegates
            every move, so without it the arrow keys would not move the row. */}
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
          <CommandList ref={highlight.listRef} className="max-h-[300px]">
            {filteredCountries.length === 0 ? (
              <CommandEmpty>{resolvedEmptyText}</CommandEmpty>
            ) : (
              <CommandGroup>
                {filteredCountries.map((country) => {
                  const isSelected = value.includes(country.code)
                  return (
                    <CommandItem
                      key={country.code}
                      value={country.code}
                      onSelect={() => handleSelect(country.code)}
                    >
                      <Flag countryCode={country.code} rounded className="mr-2 h-4 w-6 shrink-0" />
                      <div className="flex flex-col flex-1 min-w-0">
                        <span className="truncate">{country.name}</span>
                        {showNativeName && country.native !== country.name && (
                          <span className="text-xs text-muted-foreground truncate">
                            {country.native}
                          </span>
                        )}
                      </div>
                    
                      {/* Trailing and only when selected: an always-rendered
                          `opacity-0` mark indents every row to hold space one
                          row at most ever uses. Absent it, the label gets the
                          full width; present, `shrink-0` stops the label's
                          truncation exactly at the mark. */}
                      {isSelected && <Check className="ml-2 h-4 w-4 shrink-0" />}
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

// Re-export types for convenience
export type { TCountryCode } from 'countries-list';
