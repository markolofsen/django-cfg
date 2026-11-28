"use client"

import { Check, ChevronDown } from 'lucide-react'
import * as React from 'react'

import { useAppT } from '@djangocfg/i18n'
import { cn } from '../../../lib/utils'
import {
  Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList
} from '../../navigation/command'
import { Popover, PopoverContent, PopoverTrigger } from '../../overlay/popover'
import { useHighlight } from '../../../hooks';
import { FilterButton, type FilterButtonProps } from '../filter-button'

export interface FilterMenuOption {
  value: string
  label: string
  /** Matches on top of the label — a synonym, a code, a native spelling. */
  keywords?: string[]
  /** How many results this option would leave. Shown after the label. */
  count?: number
  disabled?: boolean
}

type TriggerProps = Pick<
  FilterButtonProps,
  'icon' | 'variant' | 'className' | 'disabled'
>

export interface FilterMenuProps extends TriggerProps {
  /** The question the control asks: "Body type", "Fuel". */
  label: string
  /**
   * The options to choose from. Omit and pass `children` instead to supply a
   * body of your own — a range slider, a date pair, a colour grid.
   */
  options?: FilterMenuOption[]
  /** Selected option, or `null` for none. */
  value?: string | null
  onValueChange?: (value: string | null) => void
  /**
   * When to show the search field.
   *
   * A number is a threshold on the option count; `true` / `false` force it.
   * The default is the point where the list stops fitting its own popover —
   * `.popover-scroll-region` caps at 300px and a row is ~30px, so beyond ten
   * options the reader is scrolling blind and a search field earns its place.
   * Below that it is one more thing between them and four visible answers.
   */
  searchable?: boolean | number
  searchPlaceholder?: string
  emptyText?: string
  /**
   * A body of your own, in place of `options`. The popover, the trigger and
   * its state stay this component's; what goes inside is yours.
   */
  children?: React.ReactNode
  /** Width of the popover. Defaults to the trigger's width, min 220px. */
  contentClassName?: string
}

/** The option count past which a list needs a search field. */
const SEARCHABLE_FROM = 10

/**
 * A filter control and the menu it opens.
 *
 * Pass `options` and it renders the list, adding a search field once the list
 * outgrows its popover. Pass `children` instead and the body is yours — the
 * control still owns the trigger, the popover and the open state, which is the
 * part every caller was rewriting.
 *
 * The selected option replaces the label on the trigger ("SUV", not "Body
 * type"), so a row of these reads as the current query rather than as a row of
 * unanswered questions.
 */
export function FilterMenu({
  label,
  options,
  value,
  onValueChange,
  searchable,
  searchPlaceholder,
  emptyText,
  children,
  contentClassName,
  icon,
  variant,
  className,
  disabled,
}: FilterMenuProps) {
  const t = useAppT()
  const [open, setOpen] = React.useState(false)
  const [search, setSearch] = React.useState('')
  // Opens on the current choice and scrolls to it — the same hook the
  // comboboxes use, so a long facet behaves like every other long list here.
  const highlight = useHighlight(open, value)

  const resolvedSearchPlaceholder = searchPlaceholder ?? t('ui.select.search')
  const resolvedEmptyText = emptyText ?? t('ui.select.noResults')

  const showSearch =
    typeof searchable === 'number'
      ? (options?.length ?? 0) >= searchable
      : (searchable ?? (options?.length ?? 0) >= SEARCHABLE_FROM)

  const selected = options?.find((option) => option.value === value)

  const filtered = React.useMemo(() => {
    if (!options || !search) return options ?? []
    const needle = search.toLowerCase()
    return options.filter(
      (option) =>
        option.label.toLowerCase().includes(needle) ||
        option.value.toLowerCase().includes(needle) ||
        option.keywords?.some((k) => k.toLowerCase().includes(needle))
    )
  }, [options, search])

  const handleSelect = React.useCallback(
    (next: string) => {
      // Selecting the chosen option again clears it: the trigger is the only
      // affordance a filter row has, and a dead-end "chosen" state would need
      // a second one.
      onValueChange?.(next === value ? null : next)
      setOpen(false)
    },
    [onValueChange, value]
  )

  const handleOpenChange = React.useCallback((next: boolean) => {
    setOpen(next)
    if (!next) setSearch('')
  }, [])

  return (
    <Popover open={open} onOpenChange={handleOpenChange}>
      <PopoverTrigger asChild>
        <FilterButton
          icon={icon}
          variant={variant}
          className={className}
          disabled={disabled}
          trailingIcon={ChevronDown}
          value={selected?.label}
          active={Boolean(selected)}
          aria-expanded={open}
        >
          {label}
        </FilterButton>
      </PopoverTrigger>
      <PopoverContent
        align="start"
        className={cn('w-[max(220px,var(--radix-popover-trigger-width))] p-0', contentClassName)}
      >
        {children ?? (
          <Command
            shouldFilter={false}
            value={highlight.value}
            onValueChange={highlight.setValue}
            className="flex min-h-0 flex-col"
          >
            {showSearch && (
              <CommandInput
                placeholder={resolvedSearchPlaceholder}
                className="shrink-0"
                value={search}
                onValueChange={setSearch}
              />
            )}
            <CommandList ref={highlight.listRef}>
              {filtered.length === 0 ? (
                <CommandEmpty>{resolvedEmptyText}</CommandEmpty>
              ) : (
                <CommandGroup>
                  {filtered.map((option) => (
                    <CommandItem
                      key={option.value}
                      value={option.value}
                      disabled={option.disabled}
                      onSelect={handleSelect}
                    >
                      <span className="truncate">{option.label}</span>
                      {option.count != null && (
                        <span className="ml-auto text-xs tabular-nums text-muted-foreground">
                          {option.count}
                        </span>
                      )}
                      {option.value === value && (
                        <Check className={cn('h-4 w-4 shrink-0', option.count != null ? 'ml-2' : 'ml-auto')} />
                      )}
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        )}
      </PopoverContent>
    </Popover>
  )
}
FilterMenu.displayName = 'FilterMenu'
