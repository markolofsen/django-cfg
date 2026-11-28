"use client"

import { Check, ChevronsUpDown, Search, X } from 'lucide-react';
import * as React from 'react';
import { languages, type TLanguageCode } from 'countries-list';

import { cn } from '../../lib/utils';
import { LanguageFlag } from '../specialized/flag';

import { Badge } from '../data/badge';
import { Button } from '../forms/button';
import { Checkbox } from '../forms/checkbox';
import { CONTROL_SIZE } from '../forms/control-size';
import {
  Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList
} from '../navigation/command';
import { Input } from '../forms/input';
import { Popover, PopoverContent, PopoverTrigger } from '../overlay/popover';
import { ScrollArea } from '../layout/scroll-area';
import { SELECT_TRIGGER_CLASS } from './trigger';
import { useHighlight } from '../../hooks';

export interface LanguageOption {
  code: TLanguageCode;
  name: string;
  native: string;
}

export type LanguageSelectVariant = 'dropdown' | 'inline';

/** Trigger size for the dropdown variant — mirrors Button/Input sizing.
 *  `default` = 40px form control; `sm` = 32px compact (settings rows, chips). */
export type LanguageSelectSize = 'default' | 'sm';

export interface LanguageSelectProps {
  /** Selected language codes (ISO 639-1) */
  value?: string[];
  /** Callback when selection changes */
  onChange?: (value: string[]) => void;
  /** Allow multiple selection */
  multiple?: boolean;
  /** Display variant: dropdown (popover) or inline (scrollable list) */
  variant?: LanguageSelectVariant;
  /** Trigger size for the dropdown variant (default | sm). Mirrors Button. */
  size?: LanguageSelectSize;
  /** Placeholder text (default: "Select language...") */
  placeholder?: string;
  /** Search placeholder text (default: "Search...") */
  searchPlaceholder?: string;
  /** Empty results text (default: "No languages found") */
  emptyText?: string;
  /** Additional CSS class */
  className?: string;
  /** Disable the component */
  disabled?: boolean;
  /** Max badges to display (for multiple dropdown mode) */
  maxDisplay?: number;
  /** Custom language name resolver (for i18n) */
  getLanguageName?: (code: TLanguageCode) => string;
  /** Show native name alongside translated name */
  showNativeName?: boolean;
  /** Filter to specific language codes */
  allowedLanguages?: TLanguageCode[];
  /** Exclude specific language codes */
  excludedLanguages?: TLanguageCode[];
  /** Show country-flag SVG (default: true) */
  showFlag?: boolean;
  /** Show language code (default: false) */
  showCode?: boolean;
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
 * Language Select component
 *
 * Supports:
 * - Single and multiple selection
 * - Dropdown (popover) and inline (scrollable list) variants
 * - Custom language name translations via getLanguageName prop
 * - Language filtering via allowedLanguages/excludedLanguages
 *
 * Uses ISO 639-1 language codes.
 *
 * @example Single dropdown
 * ```tsx
 * <LanguageSelect
 *   value={language ? [language] : []}
 *   onChange={(codes) => setLanguage(codes[0])}
 * />
 * ```
 *
 * @example Multiple dropdown
 * ```tsx
 * <LanguageSelect
 *   multiple
 *   value={languages}
 *   onChange={setLanguages}
 * />
 * ```
 *
 * @example Inline list with checkboxes
 * ```tsx
 * <LanguageSelect
 *   variant="inline"
 *   multiple
 *   value={languages}
 *   onChange={setLanguages}
 *   maxHeight={300}
 * />
 * ```
 *
 * @example With i18n translations
 * ```tsx
 * <LanguageSelect
 *   value={value}
 *   onChange={onChange}
 *   getLanguageName={(code) => i18nLanguages.getName(code, locale)}
 * />
 * ```
 */
export function LanguageSelect({
  value = [],
  onChange,
  multiple = false,
  variant = 'dropdown',
  size = 'default',
  placeholder,
  searchPlaceholder,
  emptyText,
  className,
  disabled = false,
  maxDisplay = 3,
  getLanguageName,
  showNativeName = false,
  allowedLanguages,
  excludedLanguages,
  showFlag = true,
  showCode = false,
  maxHeight = 300,
  showSearch = true,
  selectedCountLabel = (count: number) => `${count} selected`,
  moreItemsLabel = (count: number) => `+${count} more`,
}: LanguageSelectProps) {
  const [open, setOpen] = React.useState(false)
  const highlight = useHighlight(open, value[0])
  const [search, setSearch] = React.useState("")

  // Resolve defaults
  const resolvedPlaceholder = placeholder ?? 'Select language...'
  const resolvedSearchPlaceholder = searchPlaceholder ?? 'Search...'
  const resolvedEmptyText = emptyText ?? 'No languages found'

  // Build language options
  const allLanguages = React.useMemo<LanguageOption[]>(() => {
    let codes = Object.keys(languages) as TLanguageCode[];

    // Apply filters
    if (allowedLanguages?.length) {
      codes = codes.filter(code => allowedLanguages.includes(code));
    }
    if (excludedLanguages?.length) {
      codes = codes.filter(code => !excludedLanguages.includes(code));
    }

    return codes
      .map((code) => ({
        code,
        name: getLanguageName?.(code) ?? languages[code].name,
        native: languages[code].native,
      }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [getLanguageName, allowedLanguages, excludedLanguages]);

  const selectedLanguages = React.useMemo(
    () => allLanguages.filter((l) => value.includes(l.code)),
    [allLanguages, value]
  )

  const filteredLanguages = React.useMemo(() => {
    if (!search) return allLanguages
    const searchLower = search.toLowerCase()
    return allLanguages.filter(
      (l) =>
        l.name.toLowerCase().includes(searchLower) ||
        l.native.toLowerCase().includes(searchLower) ||
        l.code.toLowerCase().includes(searchLower)
    )
  }, [allLanguages, search])

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
    if (selectedLanguages.length === 0) {
      return <span className="text-muted-foreground">{resolvedPlaceholder}</span>
    }

    if (!multiple && selectedLanguages.length === 1) {
      const language = selectedLanguages[0]!;
      return (
        <div className="flex items-center gap-2">
          {showFlag && <LanguageFlag code={language.code} className="h-3 w-4" rounded />}
          {showCode && <span className="text-xs text-muted-foreground uppercase">{language.code}</span>}
          <span>{language.name}</span>
        </div>
      );
    }

    const displayed = selectedLanguages.slice(0, maxDisplay)
    const remaining = selectedLanguages.length - maxDisplay

    return (
      <div className="flex flex-wrap gap-1">
        {displayed.map((language) => (
          <Badge
            key={language.code}
            variant="secondary"
            className="mr-1 text-xs"
          >
            {showFlag && <LanguageFlag code={language.code} className="mr-1 h-3 w-4" rounded />}
            {showCode && <span className="mr-1 text-muted-foreground uppercase">{language.code}</span>}
            {language.name}
            <button
              className="ml-1 rounded-full hover:bg-muted-foreground/20"
              onClick={(e) => handleRemove(language.code, e)}
              disabled={disabled}
              aria-label={`Remove ${language.name}`}
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
  }, [selectedLanguages, maxDisplay, resolvedPlaceholder, disabled, multiple, handleRemove, moreItemsLabel, showFlag, showCode])

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
        {multiple && selectedLanguages.length > 0 && (
          <p className="text-sm text-muted-foreground">
            {selectedCountLabel(selectedLanguages.length)}
          </p>
        )}

        {/* Language list */}
        <ScrollArea style={{ height: maxHeight }} className="rounded-[var(--radius-popover)] border">
          <div className="p-1">
            {filteredLanguages.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                {resolvedEmptyText}
              </p>
            ) : (
              filteredLanguages.map((language) => {
                const isSelected = value.includes(language.code);
                return (
                  <div
                    key={language.code}
                    role="button"
                    tabIndex={disabled ? -1 : 0}
                    onClick={() => !disabled && handleSelect(language.code)}
                    onKeyDown={(e) => {
                      if (!disabled && (e.key === 'Enter' || e.key === ' ')) {
                        e.preventDefault();
                        handleSelect(language.code);
                      }
                    }}
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
                        onCheckedChange={() => !disabled && handleSelect(language.code)}
                        disabled={disabled}
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <div className={cn(
                        "h-4 w-4 rounded-full border-2 flex items-center justify-center",
                        isSelected ? "border-primary bg-primary" : "border-muted-foreground"
                      )}>
                        {isSelected && <div className="h-2 w-2 rounded-full bg-primary-foreground" />}
                      </div>
                    )}
                    {showFlag && (
                      <LanguageFlag code={language.code} className="h-3.5 w-5" rounded />
                    )}
                    <div className="flex flex-col flex-1 min-w-0">
                      <span className={cn('text-sm', isSelected && 'font-medium')}>
                        {language.name}
                      </span>
                      {showNativeName && language.native !== language.name && (
                        <span className="text-xs text-muted-foreground">
                          {language.native}
                        </span>
                      )}
                    </div>
                    {showCode && (
                      <span className="text-xs text-muted-foreground uppercase">
                        {language.code}
                      </span>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </ScrollArea>
      </div>
    );
  }

  // Dropdown variant (displayValue is memoized above, before the inline guard)
  const triggerSize = size === 'sm' ? 'sm' : 'default';
  // Single-select: a fixed-height pill (the Button size sets height).
  // Multiple: allow growth so wrapped badges aren't clipped, never shorter than
  // the fixed control of the same size.
  const triggerSizeClass = multiple
    ? cn('h-auto', CONTROL_SIZE[triggerSize].minHeight, size === 'sm' ? 'py-1' : 'py-2')
    : size === 'sm' && 'text-xs';

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
          size={triggerSize}
          role="combobox"
          aria-expanded={open}
          className={cn(SELECT_TRIGGER_CLASS, triggerSizeClass, className)}
          disabled={disabled}
        >
          <div className="flex-1 text-left overflow-hidden">
            {displayValue}
          </div>
          <ChevronsUpDown className={cn("ml-2 shrink-0 opacity-50", size === 'sm' ? "h-3.5 w-3.5" : "h-4 w-4")} />
        </Button>
      </PopoverTrigger>
      {/* The list must stay readable even when the trigger is a narrow
          status-bar/settings pill: grow to the trigger width but never below a
          legible min, so language names aren't clipped to "En…". */}
      <PopoverContent
        className="w-auto min-w-[var(--radix-popover-trigger-width)] p-0 [--lang-min:11rem] [min-width:max(var(--radix-popover-trigger-width),var(--lang-min))]"
        align="start"
      >
        {/* Controlled highlight. `onValueChange` is mandatory alongside it:
            with a controlled `value` cmdk stores nothing itself and delegates
            every move, so without it the arrow keys would not move the row. */}
        <Command
          shouldFilter={false}
          value={highlight.value}
          onValueChange={highlight.setValue}
          className="flex flex-col"
        >
          {showSearch && (
            <CommandInput
              placeholder={resolvedSearchPlaceholder}
              className="shrink-0"
              value={search}
              onValueChange={setSearch}
            />
          )}
          <CommandList ref={highlight.listRef} className="max-h-[300px] overflow-y-auto">
            {filteredLanguages.length === 0 ? (
              <CommandEmpty>{resolvedEmptyText}</CommandEmpty>
            ) : (
              <CommandGroup>
                {filteredLanguages.map((language) => {
                  const isSelected = value.includes(language.code)
                  return (
                    <CommandItem
                      key={language.code}
                      value={language.code}
                      onSelect={() => handleSelect(language.code)}
                    >
                      {showFlag && (
                        <LanguageFlag code={language.code} className="mr-2 h-3.5 w-5" rounded />
                      )}
                      <div className="flex flex-col flex-1 min-w-0">
                        <span className="truncate">{language.name}</span>
                        {showNativeName && language.native !== language.name && (
                          <span className="text-xs text-muted-foreground truncate">
                            {language.native}
                          </span>
                        )}
                      </div>
                      {showCode && (
                        <span className="text-xs text-muted-foreground uppercase ml-2">
                          {language.code}
                        </span>
                      )}
                    
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
export type { TLanguageCode } from 'countries-list';
export { LANGUAGE_TO_COUNTRY } from '../specialized/flag';
