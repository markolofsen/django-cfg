'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { ChevronsUpDown, Check, X } from 'lucide-react';
import {
  Popover,
  PopoverTrigger,
} from '@djangocfg/ui-core/components';
import { ComboboxProvider, useComboboxContext } from '../context';
import type {
  ComboboxProps,
  ComboboxTriggerProps,
  ComboboxInputProps,
  ComboboxListProps,
  ComboboxItemProps,
  ComboboxEmptyProps,
  ComboboxOption,
} from '../types';

function defaultFilter(options: ComboboxOption[], search: string): ComboboxOption[] {
  const q = search.toLowerCase();
  return options.filter(
    (o) =>
      o.label.toLowerCase().includes(q) ||
      o.value.toLowerCase().includes(q) ||
      o.description?.toLowerCase().includes(q)
  );
}

export function Combobox({
  children,
  options,
  value: valueProp,
  defaultValue = null,
  multiple = false,
  placeholder = 'Select...',
  onChange,
  onFilter = defaultFilter,
  disabled = false,
  className,
}: ComboboxProps) {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState('');
  const [highlightedIndex, setHighlightedIndex] = React.useState(0);
  const [internalValue, setInternalValue] = React.useState<string | string[] | null>(defaultValue);

  const value = valueProp !== undefined ? valueProp : internalValue;

  const filteredOptions = React.useMemo(
    () => onFilter(options, search),
    [options, search, onFilter]
  );

  const selectOption = React.useCallback(
    (option: ComboboxOption) => {
      if (multiple) {
        const current = Array.isArray(value) ? value : [];
        const exists = current.includes(option.value);
        const next = exists
          ? current.filter((v) => v !== option.value)
          : [...current, option.value];
        setInternalValue(next);
        onChange?.(next);
        if (!exists) {
          setSearch('');
        }
      } else {
        setInternalValue(option.value);
        onChange?.(option.value);
        setOpen(false);
        setSearch('');
      }
    },
    [multiple, value, onChange]
  );

  const removeValue = React.useCallback(
    (val: string) => {
      if (multiple) {
        const current = Array.isArray(value) ? value : [];
        const next = current.filter((v) => v !== val);
        setInternalValue(next);
        onChange?.(next);
      } else {
        setInternalValue(null);
        onChange?.(null);
      }
    },
    [multiple, value, onChange]
  );

  const isSelected = React.useCallback(
    (val: string) => {
      if (multiple) {
        return Array.isArray(value) && value.includes(val);
      }
      return value === val;
    },
    [multiple, value]
  );

  const ctxValue = React.useMemo(
    () => ({
      open,
      search,
      value,
      multiple,
      highlightedIndex,
      options,
      filteredOptions,
      setOpen,
      setSearch,
      setHighlightedIndex,
      selectOption,
      removeValue,
      isSelected,
    }),
    [
      open,
      search,
      value,
      multiple,
      highlightedIndex,
      options,
      filteredOptions,
      selectOption,
      removeValue,
      isSelected,
    ]
  );

  return (
    <ComboboxProvider value={ctxValue}>
      <div
        data-slot="combobox"
        data-disabled={disabled ? 'true' : undefined}
        className={cn('relative', className)}
      >
        {children ?? (
          <>
            <ComboboxTrigger placeholder={placeholder} />
            <ComboboxList />
          </>
        )}
      </div>
    </ComboboxProvider>
  );
}
Combobox.displayName = 'Combobox';

export function ComboboxTrigger({
  children,
  className,
  placeholder = 'Select...',
  ...props
}: ComboboxTriggerProps & { placeholder?: string }) {
  const { open, setOpen, value, multiple, options, removeValue } = useComboboxContext();

  /**
   * Label AND value together, never two parallel arrays.
   *
   * This was a `.map(...).filter(Boolean)` over the labels, while the chip's
   * remove button indexed the UNFILTERED `value` array with the FILTERED
   * list's index. One option with an empty label — or a raw `''` value falling
   * through the `?? v` — shifts every index after it, and clicking the ✕ on
   * one chip removes a different selection. Carrying the pair through the
   * filter makes the two impossible to misalign.
   */
  const selected = React.useMemo<Array<{ label: string; value: string }>>(() => {
    if (multiple) {
      const vals = Array.isArray(value) ? value : [];
      return vals
        .map((v) => ({ label: options.find((o) => o.value === v)?.label ?? v, value: v }))
        .filter((entry) => Boolean(entry.label));
    }
    // Single-select: the context types `value` as `string | string[]`, so an
    // array here would be a caller error rather than a state to render.
    if (!value || Array.isArray(value)) return [];
    const opt = options.find((o) => o.value === value);
    return [{ label: opt ? opt.label : value, value }];
  }, [value, multiple, options]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          type="button"
          data-slot="combobox-trigger"
          role="combobox"
          aria-expanded={open}
          className={cn(
            'flex h-9 w-full items-center justify-between rounded-md border border-input',
            'bg-background px-3 py-2 text-sm shadow-sm ring-offset-background',
            'placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring',
            'disabled:cursor-not-allowed disabled:opacity-50',
            className
          )}
          {...props}
        >
          {children ?? (
            <div className="flex flex-1 items-center gap-1 overflow-hidden">
              {selected.length === 0 ? (
                <span className="text-muted-foreground">{placeholder}</span>
              ) : (
                selected.map((entry) => (
                  <span
                    key={entry.value}
                    className="inline-flex items-center gap-1 rounded bg-muted px-1.5 py-0.5 text-xs"
                  >
                    {entry.label}
                    {multiple && (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeValue(entry.value);
                        }}
                        className="rounded-sm hover:bg-muted-foreground/20"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </span>
                ))
              )}
            </div>
          )}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </button>
      </PopoverTrigger>
    </Popover>
  );
}
ComboboxTrigger.displayName = 'ComboboxTrigger';

export function ComboboxInput({ className, onChange, onKeyDown, ...props }: ComboboxInputProps) {
  const {
    search,
    setSearch,
    setHighlightedIndex,
    highlightedIndex,
    filteredOptions,
    selectOption,
    setOpen,
  } = useComboboxContext();

  const handleChange = React.useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setSearch(e.target.value);
      setHighlightedIndex(0);
      onChange?.(e);
    },
    [setSearch, setHighlightedIndex, onChange]
  );

  const handleKeyDown = React.useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setHighlightedIndex((prev: number) =>
            prev < filteredOptions.length - 1 ? prev + 1 : 0
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setHighlightedIndex((prev: number) =>
            prev > 0 ? prev - 1 : filteredOptions.length - 1
          );
          break;
        case 'Enter':
          e.preventDefault();
          if (filteredOptions[highlightedIndex]) {
            selectOption(filteredOptions[highlightedIndex]);
          }
          break;
        case 'Escape':
          setOpen(false);
          break;
        default:
          onKeyDown?.(e);
      }
    },
    [filteredOptions, highlightedIndex, selectOption, setOpen, setHighlightedIndex, onKeyDown]
  );

  return (
    <input
      data-slot="combobox-input"
      className={cn(
        'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm',
        'placeholder:text-muted-foreground focus-visible:outline-none',
        className
      )}
      value={search}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      {...props}
    />
  );
}
ComboboxInput.displayName = 'ComboboxInput';

export function ComboboxList({ children, className, ...props }: ComboboxListProps) {
  const { open, filteredOptions } = useComboboxContext();

  if (!open) return null;

  return (
    <div
      data-slot="combobox-list"
      className={cn(
        'absolute z-50 mt-1 w-full rounded-md border bg-popover p-1 text-popover-foreground shadow-md',
        className
      )}
      {...props}
    >
      <div className="flex flex-col gap-0.5 max-h-60 overflow-y-auto">
        {children ??
          filteredOptions.map((option, index) => (
            <ComboboxItem key={option.value} option={option} index={index} />
          ))}
      </div>
    </div>
  );
}
ComboboxList.displayName = 'ComboboxList';

export function ComboboxItem({
  option,
  index,
  className,
  onClick,
  ...props
}: ComboboxItemProps) {
  const { highlightedIndex, selectOption, setHighlightedIndex, isSelected } =
    useComboboxContext();
  const isHighlighted = highlightedIndex === index;
  const selected = isSelected(option.value);

  const handleClick = React.useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      e.preventDefault();
      selectOption(option);
      onClick?.(e);
    },
    [option, selectOption, onClick]
  );

  const handlePointerEnter = React.useCallback(() => {
    setHighlightedIndex(index);
  }, [index, setHighlightedIndex]);

  return (
    <div
      data-slot="combobox-item"
      data-value={option.value}
      data-highlighted={isHighlighted ? 'true' : undefined}
      data-selected={selected ? 'true' : undefined}
      data-disabled={option.disabled ? 'true' : undefined}
      onClick={handleClick}
      onPointerEnter={handlePointerEnter}
      className={cn(
        'relative flex items-center gap-2 rounded-sm px-2 py-1.5 text-sm cursor-pointer',
        'hover:bg-accent hover:text-accent-foreground',
        isHighlighted && 'bg-accent text-accent-foreground',
        option.disabled && 'pointer-events-none opacity-50',
        className
      )}
      {...props}
    >
      <span className="flex h-4 w-4 items-center justify-center">
        {selected && <Check className="h-4 w-4" />}
      </span>
      {option.icon && <span className="shrink-0">{option.icon}</span>}
      <div className="flex flex-col">
        <span className="truncate">{option.label}</span>
        {option.description && (
          <span className="text-xs text-muted-foreground">{option.description}</span>
        )}
      </div>
    </div>
  );
}
ComboboxItem.displayName = 'ComboboxItem';

export function ComboboxEmpty({ children, className, ...props }: ComboboxEmptyProps) {
  const { filteredOptions } = useComboboxContext();

  if (filteredOptions.length > 0) return null;

  return (
    <div
      data-slot="combobox-empty"
      className={cn('px-2 py-4 text-center text-sm text-muted-foreground', className)}
      {...props}
    >
      {children ?? 'No results found.'}
    </div>
  );
}
ComboboxEmpty.displayName = 'ComboboxEmpty';
