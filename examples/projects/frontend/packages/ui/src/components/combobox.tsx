"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "../lib/utils"
import { Button } from "./button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "./command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "./popover"

export interface ComboboxOption {
  value: string
  label: string
  description?: string
  disabled?: boolean
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
}

export function Combobox({
  options,
  value,
  onValueChange,
  placeholder = "Select option...",
  searchPlaceholder = "Search...",
  emptyText = "No results found.",
  className,
  disabled = false,
  renderOption,
  renderValue,
}: ComboboxProps) {
  const [open, setOpen] = React.useState(false)
  const [search, setSearch] = React.useState("")
  const scrollRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (scrollRef.current && open) {
      // Force scrollable styles with !important
      const el = scrollRef.current
      el.style.cssText = `
        max-height: 300px !important;
        overflow-y: scroll !important;
        overflow-x: hidden !important;
        -webkit-overflow-scrolling: touch !important;
        overscroll-behavior: contain !important;
      `
    }
  }, [open])

  const selectedOption = React.useMemo(
    () => options.find((option) => option.value === value),
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
            "w-full justify-between",
            !value && "text-muted-foreground",
            className
          )}
          disabled={disabled}
        >
          {renderValue && selectedOption
            ? renderValue(selectedOption)
            : selectedOption
            ? selectedOption.label
            : placeholder}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0" align="start">
        <Command shouldFilter={false} className="flex flex-col">
          <CommandInput
            placeholder={searchPlaceholder}
            className="shrink-0"
            value={search}
            onValueChange={setSearch}
          />
          <div
            ref={scrollRef}
            tabIndex={-1}
            className="overflow-y-scroll overflow-x-hidden"
            style={{
              maxHeight: '300px',
              minHeight: '100px',
            }}
            onWheel={(e) => {
              e.stopPropagation()
            }}
          >
            <CommandList className="!max-h-none !overflow-visible" style={{ pointerEvents: 'auto' }}>
              {filteredOptions.length === 0 ? (
                <CommandEmpty>{emptyText}</CommandEmpty>
              ) : (
                <CommandGroup className="!overflow-visible" style={{ pointerEvents: 'auto' }}>
                  {filteredOptions.map((option) => (
                  <CommandItem
                    key={option.value}
                    value={option.value}
                    onSelect={(currentValue) => {
                      if (!option.disabled) {
                        onValueChange?.(currentValue === value ? "" : currentValue)
                        setOpen(false)
                      }
                    }}
                    disabled={option.disabled}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4 shrink-0",
                        value === option.value ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {renderOption ? (
                      renderOption(option)
                    ) : (
                      <div className="flex flex-col flex-1 min-w-0">
                        <span className="truncate">{option.label}</span>
                        {option.description && (
                          <span className="text-xs text-muted-foreground truncate">
                            {option.description}
                          </span>
                        )}
                      </div>
                    )}
                  </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </div>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
