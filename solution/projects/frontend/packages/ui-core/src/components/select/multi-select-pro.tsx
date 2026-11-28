"use client"

import { cva, type VariantProps } from 'class-variance-authority';
import { Check, ChevronsUpDown, X, XCircle } from 'lucide-react';
import * as React from 'react';

import { useAppT } from '@djangocfg/i18n';
import { Badge } from '../data/badge';
import { Button } from '../forms/button';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator } from '../navigation/command';
import { Popover, PopoverContent, PopoverTrigger } from '../overlay/popover';
import { Separator } from '../layout/separator';
import { cn } from '../../lib';
import { SELECT_TRIGGER_MULTI_CLASS } from './trigger';

// ==================== TYPES ====================

export interface MultiSelectProOption {
  label: string
  value: string
  description?: string  // Optional subtitle/description text shown below label
  icon?: React.ComponentType<{ className?: string }>
  disabled?: boolean
  style?: {
    badgeColor?: string
    iconColor?: string
    gradient?: string
  }
}

export interface MultiSelectProGroup {
  heading: string
  options: MultiSelectProOption[]
}

export interface AnimationConfig {
  badgeAnimation?: "bounce" | "pulse" | "wiggle" | "fade" | "slide" | "none"
  popoverAnimation?: "scale" | "slide" | "fade" | "flip" | "none"
  optionHoverAnimation?: "highlight" | "scale" | "glow" | "none"
  duration?: number
  delay?: number
}

export interface ResponsiveConfig {
  mobile?: { maxDisplay?: number; compact?: boolean }
  tablet?: { maxDisplay?: number; compact?: boolean }
  desktop?: { maxDisplay?: number; compact?: boolean }
}

export interface MultiSelectProRef {
  reset: () => void
  getSelectedValues: () => string[]
  setSelectedValues: (values: string[]) => void
  clear: () => void
  focus: () => void
}

// ==================== VARIANTS ====================

const multiSelectVariants = cva(
  SELECT_TRIGGER_MULTI_CLASS,
  {
    variants: {
      variant: {
        default: "border-border bg-background hover:bg-accent/50",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        inverted: "bg-primary text-primary-foreground hover:bg-primary/90",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

const badgeAnimations = {
  bounce: "animate-bounce",
  pulse: "animate-pulse",
  wiggle: "animate-wiggle",
  fade: "animate-fadeIn",
  slide: "animate-slideIn",
  none: "",
}

const popoverAnimations = {
  scale: "data-[state=open]:animate-scaleIn data-[state=closed]:animate-scaleOut",
  slide: "data-[state=open]:animate-slideDown data-[state=closed]:animate-slideUp",
  fade: "data-[state=open]:animate-fadeIn data-[state=closed]:animate-fadeOut",
  flip: "data-[state=open]:animate-flipIn data-[state=closed]:animate-flipOut",
  none: "",
}

// ==================== PROPS ====================

export interface MultiSelectProProps extends VariantProps<typeof multiSelectVariants> {
  options: MultiSelectProOption[] | MultiSelectProGroup[]
  onValueChange?: (value: string[]) => void
  defaultValue?: string[]
  placeholder?: string
  variant?: "default" | "secondary" | "destructive" | "inverted"
  animation?: number
  animationConfig?: AnimationConfig
  maxCount?: number
  modalPopover?: boolean
  asChild?: boolean
  className?: string
  hideSelectAll?: boolean
  searchable?: boolean
  emptyIndicator?: React.ReactNode
  autoSize?: boolean
  singleLine?: boolean
  popoverClassName?: string
  disabled?: boolean
  responsive?: boolean | ResponsiveConfig
  minWidth?: string
  maxWidth?: string
  deduplicateOptions?: boolean
  resetOnDefaultValueChange?: boolean
  closeOnSelect?: boolean
}

// ==================== HELPERS ====================

function isGroupedOptions(options: MultiSelectProOption[] | MultiSelectProGroup[]): options is MultiSelectProGroup[] {
  return options.length > 0 && 'heading' in options[0]!
}

function flattenOptions(options: MultiSelectProOption[] | MultiSelectProGroup[]): MultiSelectProOption[] {
  if (isGroupedOptions(options)) {
    return options.flatMap((group) => group.options)
  }
  return options
}

function deduplicateOptions(options: MultiSelectProOption[]): MultiSelectProOption[] {
  const seen = new Set<string>()
  return options.filter((option) => {
    if (seen.has(option.value)) {
      return false
    }
    seen.add(option.value)
    return true
  })
}

// ==================== COMPONENT ====================

export const MultiSelectPro = React.forwardRef<MultiSelectProRef, MultiSelectProProps>(
  (
    {
      options,
      onValueChange,
      defaultValue = [],
      placeholder,
      variant = "default",
      animation = 0,
      animationConfig,
      maxCount = 3,
      modalPopover = false,
      className,
      hideSelectAll = false,
      searchable = true,
      emptyIndicator,
      autoSize = false,
      singleLine = false,
      popoverClassName,
      disabled = false,
      responsive = false,
      minWidth,
      maxWidth,
      deduplicateOptions: shouldDeduplicate = false,
      resetOnDefaultValueChange = true,
      closeOnSelect = false,
    },
    ref
  ) => {
    const t = useAppT()
    const [open, setOpen] = React.useState(false)
    const [selectedValues, setSelectedValues] = React.useState<string[]>(defaultValue)
    const [search, setSearch] = React.useState("")
    const buttonRef = React.useRef<HTMLButtonElement>(null)
    const [announcements, setAnnouncements] = React.useState<string>("")
    // Cache selected options to persist them when they disappear from current options
    const [selectedOptionsCache, setSelectedOptionsCache] = React.useState<Map<string, MultiSelectProOption>>(new Map())

    // Prepare translations
    const translations = React.useMemo(() => ({
      placeholder: placeholder ?? t('ui.select.placeholder'),
      search: t('ui.select.search'),
      selectAll: t('ui.select.selectAll'),
      clearAll: t('ui.select.clearAll'),
      noResults: t('ui.select.noResults'),
      moreItems: (count: number) => t('ui.select.moreItems', { count }),
      remove: (label: string) => t('ui.actions.remove', { item: label }),
    }), [placeholder, t])

    // Process options
    const flatOptions = React.useMemo(() => {
      const flat = flattenOptions(options)
      return shouldDeduplicate ? deduplicateOptions(flat) : flat
    }, [options, shouldDeduplicate])

    // Update cache whenever new options appear
    React.useEffect(() => {
      setSelectedOptionsCache(prev => {
        const updated = new Map(prev)
        flatOptions.forEach(option => {
          if (selectedValues.includes(option.value)) {
            updated.set(option.value, option)
          }
        })
        return updated
      })
    }, [flatOptions, selectedValues])

    // Responsive configuration (reserved for future use)
    const _responsiveConfig = React.useMemo((): ResponsiveConfig => {
      if (typeof responsive === 'boolean') {
        return responsive
          ? {
              mobile: { maxDisplay: 2, compact: true },
              tablet: { maxDisplay: 4, compact: false },
              desktop: { maxDisplay: 6, compact: false },
            }
          : {}
      }
      return responsive || {}
    }, [responsive])

    // Animation configuration
    const animConfig = React.useMemo(
      (): AnimationConfig => ({
        badgeAnimation: animationConfig?.badgeAnimation || (animation > 0 ? "bounce" : "none"),
        popoverAnimation: animationConfig?.popoverAnimation || "scale",
        optionHoverAnimation: animationConfig?.optionHoverAnimation || "highlight",
        // `??`: a caller asking for duration 0 means "no animation",
        // and `||` swallowed it into the 0.3 default.
        duration: animationConfig?.duration ?? (animation > 0 ? animation : 0.3),
        delay: animationConfig?.delay || 0,
      }),
      [animation, animationConfig]
    )

    // Reset on defaultValue change
    React.useEffect(() => {
      if (resetOnDefaultValueChange) {
        setSelectedValues(defaultValue)
      }
    }, [defaultValue, resetOnDefaultValueChange])

    // Announce changes for screen readers
    // One timer, cleared on unmount: the announcement is transient UI state,
    // and stacking a timer per change clears it early for the latest message.
    const announceTimerRef = React.useRef<ReturnType<typeof setTimeout> | null>(null)
    React.useEffect(
      () => () => {
        if (announceTimerRef.current) clearTimeout(announceTimerRef.current)
      },
      []
    )

    const announce = React.useCallback((message: string) => {
      setAnnouncements(message)
      if (announceTimerRef.current) clearTimeout(announceTimerRef.current)
      announceTimerRef.current = setTimeout(() => {
        announceTimerRef.current = null
        setAnnouncements("")
      }, 1000)
    }, [])

    // Toggle selection
    const toggleOption = React.useCallback(
      (value: string) => {
        const isRemoving = selectedValues.includes(value)
        const newValues = isRemoving
          ? selectedValues.filter((v) => v !== value)
          : [...selectedValues, value]

        setSelectedValues(newValues)
        onValueChange?.(newValues)

        const option = flatOptions.find((o) => o.value === value)
        if (option) {
          // Add to cache when selecting
          if (!isRemoving) {
            setSelectedOptionsCache(prev => new Map(prev).set(value, option))
          }

          announce(
            isRemoving
              ? `Removed ${option.label}`
              : `Added ${option.label}`
          )
        }

        if (closeOnSelect) {
          setOpen(false)
        }
      },
      [selectedValues, onValueChange, flatOptions, announce, closeOnSelect]
    )

    // Select all
    const handleSelectAll = React.useCallback(() => {
      const allValues = flatOptions.filter((o) => !o.disabled).map((o) => o.value)
      setSelectedValues(allValues)
      onValueChange?.(allValues)

      // Cache all selected options
      setSelectedOptionsCache(prev => {
        const updated = new Map(prev)
        flatOptions.forEach(option => {
          if (!option.disabled) {
            updated.set(option.value, option)
          }
        })
        return updated
      })

      announce(`Selected all ${allValues.length} options`)
    }, [flatOptions, onValueChange, announce])

    // Clear all
    const handleClearAll = React.useCallback(() => {
      setSelectedValues([])
      onValueChange?.([])
      announce("Cleared all selections")
    }, [onValueChange, announce])

    // Imperative methods
    React.useImperativeHandle(ref, () => ({
      reset: () => {
        setSelectedValues(defaultValue)
        announce("Reset to default values")
      },
      getSelectedValues: () => selectedValues,
      setSelectedValues: (values: string[]) => {
        setSelectedValues(values)
        onValueChange?.(values)
      },
      clear: handleClearAll,
      focus: () => buttonRef.current?.focus(),
    }))

    // Filter options
    const filteredOptions = React.useMemo(() => {
      if (!search) return options
      const searchLower = search.toLowerCase()

      if (isGroupedOptions(options)) {
        return options
          .map((group) => ({
            ...group,
            options: group.options.filter(
              (option) =>
                option.label.toLowerCase().includes(searchLower) ||
                option.value.toLowerCase().includes(searchLower)
            ),
          }))
          .filter((group) => group.options.length > 0)
      }

      return options.filter(
        (option) =>
          option.label.toLowerCase().includes(searchLower) ||
          option.value.toLowerCase().includes(searchLower)
      )
    }, [options, search])

    // Selected options for display - use cache as fallback
    const selectedOptions = React.useMemo(
      () => selectedValues.map(value => {
        // First try to find in current options
        const option = flatOptions.find(o => o.value === value)
        // If not found, fallback to cache
        return option || selectedOptionsCache.get(value)
      }).filter((option): option is MultiSelectProOption => option !== undefined),
      [flatOptions, selectedValues, selectedOptionsCache]
    )

    // Render badge with custom styles
    const renderBadge = React.useCallback((option: MultiSelectProOption, index: number) => {
      const { style, icon: Icon } = option
      const badgeStyle: React.CSSProperties = {}

      if (style?.gradient) {
        badgeStyle.background = style.gradient
        badgeStyle.color = style.iconColor || "white"
      } else if (style?.badgeColor) {
        badgeStyle.backgroundColor = style.badgeColor
        badgeStyle.color = style.iconColor || "white"
      }

      const animationClass = animConfig.badgeAnimation
        ? badgeAnimations[animConfig.badgeAnimation]
        : ""

      return (
        <Badge
          key={option.value}
          variant={variant === "default" ? "secondary" : "outline"}
          className={cn(
            "mr-1 mb-1 text-xs gap-1 flex items-center",
            animationClass
          )}
          style={{
            ...badgeStyle,
            animationDelay: `${(animConfig.delay || 0) * index}s`,
            animationDuration: `${animConfig.duration}s`,
          }}
        >
          {Icon && <Icon className="h-3 w-3" />}
          <span>{option.label}</span>
          {!disabled && (
            <button
              className="ml-1 rounded-full hover:bg-muted-foreground/20 focus:outline-none focus:ring-1 focus:ring-ring"
              onClick={(e) => {
                e.stopPropagation()
                toggleOption(option.value)
              }}
              aria-label={translations.remove(option.label)}
            >
              <X className="h-3 w-3" />
            </button>
          )}
        </Badge>
      )
    }, [animConfig, variant, disabled, toggleOption, translations])

    // Display value
    const displayValue = React.useMemo(() => {
      if (selectedOptions.length === 0) {
        return <span className="text-muted-foreground">{translations.placeholder}</span>
      }

      const displayed = selectedOptions.slice(0, maxCount)
      const remaining = selectedOptions.length - maxCount

      return (
        <div className={cn("flex gap-1", singleLine ? "flex-nowrap overflow-x-auto" : "flex-wrap")}>
          {displayed.map((option, index) => renderBadge(option, index))}
          {remaining > 0 && (
            <Badge variant="outline" className="text-xs">
              {translations.moreItems(remaining)}
            </Badge>
          )}
        </div>
      )
    }, [selectedOptions, maxCount, translations, singleLine, renderBadge])

    // Render options
    const renderOptions = () => {
      if (isGroupedOptions(filteredOptions)) {
        return filteredOptions.map((group, groupIndex) => (
          <React.Fragment key={group.heading}>
            {groupIndex > 0 && <CommandSeparator />}
            <CommandGroup heading={group.heading}>
              {group.options.map((option) => {
                const isSelected = selectedValues.includes(option.value)
                const Icon = option.icon

                return (
                  <CommandItem
                    key={option.value}
                    value={option.value}
                    onSelect={() => !option.disabled && toggleOption(option.value)}
                    disabled={option.disabled}
                    className={cn(
                      "cursor-pointer",
                      option.disabled && "opacity-50 cursor-not-allowed"
                    )}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4 shrink-0",
                        isSelected ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {Icon && <Icon className="mr-2 h-4 w-4" />}
                    <div className="flex-1 flex flex-col gap-0.5">
                      <span>{option.label}</span>
                      {option.description && (
                        <span className="text-xs text-muted-foreground">{option.description}</span>
                      )}
                    </div>
                  </CommandItem>
                )
              })}
            </CommandGroup>
          </React.Fragment>
        ))
      }

      return (
        <CommandGroup>
          {(filteredOptions as MultiSelectProOption[]).map((option) => {
            const isSelected = selectedValues.includes(option.value)
            const Icon = option.icon

            return (
              <CommandItem
                key={option.value}
                value={option.value}
                onSelect={() => !option.disabled && toggleOption(option.value)}
                disabled={option.disabled}
                className={cn(
                  "cursor-pointer",
                  option.disabled && "opacity-50 cursor-not-allowed"
                )}
              >
                <Check
                  className={cn(
                    "mr-2 h-4 w-4 shrink-0",
                    isSelected ? "opacity-100" : "opacity-0"
                  )}
                />
                {Icon && <Icon className="mr-2 h-4 w-4" />}
                <div className="flex-1 flex flex-col gap-0.5">
                  <span>{option.label}</span>
                  {option.description && (
                    <span className="text-xs text-muted-foreground">{option.description}</span>
                  )}
                </div>
              </CommandItem>
            )
          })}
        </CommandGroup>
      )
    }

    const containerStyle: React.CSSProperties = {}
    if (minWidth) containerStyle.minWidth = minWidth
    if (maxWidth) containerStyle.maxWidth = maxWidth

    return (
      <div style={containerStyle} className="relative">
        {/* ARIA Live Region for announcements */}
        <div
          role="status"
          aria-live="polite"
          aria-atomic="true"
          className="sr-only"
        >
          {announcements}
        </div>

        <Popover
          open={open}
          onOpenChange={(isOpen) => {
            if (!disabled) {
              setOpen(isOpen)
              if (isOpen) {
                announce(`Dropdown opened. ${flatOptions.length} options available`)
              } else {
                setSearch("")
                announce("Dropdown closed")
              }
            }
          }}
          modal={modalPopover}
        >
          <PopoverTrigger asChild>
            <Button
              ref={buttonRef}
              variant="outline"
              role="combobox"
              aria-expanded={open}
              aria-label={placeholder}
              className={cn(multiSelectVariants({ variant }), className)}
              disabled={disabled}
            >
              <div className={cn("flex-1 text-left", autoSize ? "" : "overflow-hidden")}>
                {displayValue}
              </div>
              <div className="flex items-center gap-1 ml-2">
                {selectedValues.length > 0 && !disabled && (
                  <span
                    role="button"
                    tabIndex={0}
                    onClick={(e) => {
                      e.stopPropagation()
                      handleClearAll()
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault()
                        e.stopPropagation()
                        handleClearAll()
                      }
                    }}
                    className="rounded-full hover:bg-muted-foreground/20 focus:outline-none focus:ring-1 focus:ring-ring"
                    aria-label={translations.clearAll}
                  >
                    <XCircle className="h-4 w-4 shrink-0 opacity-50" />
                  </span>
                )}
                <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50" />
              </div>
            </Button>
          </PopoverTrigger>
          <PopoverContent
            className={cn(
              "w-[var(--radix-popover-trigger-width)] p-0",
              animConfig.popoverAnimation ? popoverAnimations[animConfig.popoverAnimation] : "",
              popoverClassName
            )}
            align="start"
            style={{
              animationDuration: `${animConfig.duration}s`,
            }}
          >
            <Command shouldFilter={false}>
              {searchable && (
                <CommandInput
                  placeholder={translations.search}
                  value={search}
                  onValueChange={setSearch}
                />
              )}
              <CommandList>
                {!hideSelectAll && !isGroupedOptions(options) && (
                  <>
                    <CommandGroup>
                      <CommandItem
                        onSelect={handleSelectAll}
                        className="cursor-pointer justify-center font-medium"
                      >
                        {translations.selectAll}
                      </CommandItem>
                    </CommandGroup>
                    <Separator />
                  </>
                )}

                {filteredOptions.length === 0 ? (
                  <CommandEmpty>
                    {emptyIndicator || translations.noResults}
                  </CommandEmpty>
                ) : (
                  renderOptions()
                )}
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      </div>
    )
  }
)

MultiSelectPro.displayName = "MultiSelectPro"
