'use client'

import { format } from 'date-fns';
import { CalendarIcon } from 'lucide-react';
import * as React from 'react';

import { useAppT } from '@djangocfg/i18n';
import { cn } from '../../../lib/utils';
import { Button } from '../../forms/button';
import { Popover, PopoverContent, PopoverTrigger } from '../../overlay/popover';
import { Calendar } from './calendar';

import type { DateRange as RDPDateRange } from 'react-day-picker'

// =============================================================================
// DatePicker - Single date selection with popover
// =============================================================================

export interface DatePickerProps {
  /** Selected date */
  value?: Date
  /** Callback when date changes */
  onChange?: (date: Date | undefined) => void
  /** Placeholder text when no date selected */
  placeholder?: string
  /** Date format string (date-fns format) */
  dateFormat?: string
  /** Disable the picker */
  disabled?: boolean
  /** Minimum selectable date */
  fromDate?: Date
  /** Maximum selectable date */
  toDate?: Date
  /** Additional class names for the trigger button */
  className?: string
  /** Button variant */
  variant?: 'default' | 'outline' | 'ghost'
  /** Align popover */
  align?: 'start' | 'center' | 'end'
}

const DatePicker = React.forwardRef<HTMLButtonElement, DatePickerProps>(
  (
    {
      value,
      onChange,
      placeholder,
      dateFormat = 'PPP',
      disabled = false,
      fromDate,
      toDate,
      className,
      variant = 'outline',
      align = 'start',
    },
    ref
  ) => {
    const t = useAppT()
    const [open, setOpen] = React.useState(false)

    const resolvedPlaceholder = placeholder ?? t('ui.datetime.pickDate')

    const handleSelect = (date: Date | undefined) => {
      onChange?.(date)
      setOpen(false)
    }

    return (
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            ref={ref}
            variant={variant}
            disabled={disabled}
            className={cn(
              'w-full justify-start text-left font-normal',
              !value && 'text-muted-foreground',
              className
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {value ? format(value, dateFormat) : resolvedPlaceholder}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align={align}>
          <Calendar
            mode="single"
            selected={value}
            onSelect={handleSelect}
            disabled={disabled}
            fromDate={fromDate}
            toDate={toDate}
            initialFocus
          />
        </PopoverContent>
      </Popover>
    )
  }
)
DatePicker.displayName = 'DatePicker'

// =============================================================================
// DateRangePicker - Date range selection with popover
// =============================================================================

/** Date range type - re-exported from react-day-picker for convenience */
export type DateRange = RDPDateRange

export interface DateRangePickerProps {
  /** Selected date range */
  value?: DateRange
  /** Callback when range changes */
  onChange?: (range: DateRange | undefined) => void
  /** Placeholder text when no range selected */
  placeholder?: string
  /** Date format string (date-fns format) */
  dateFormat?: string
  /** Disable the picker */
  disabled?: boolean
  /** Minimum selectable date */
  fromDate?: Date
  /** Maximum selectable date */
  toDate?: Date
  /** Number of months to display */
  numberOfMonths?: number
  /** Additional class names for the trigger button */
  className?: string
  /** Button variant */
  variant?: 'default' | 'outline' | 'ghost'
  /** Align popover */
  align?: 'start' | 'center' | 'end'
}

const DateRangePicker = React.forwardRef<HTMLButtonElement, DateRangePickerProps>(
  (
    {
      value,
      onChange,
      placeholder,
      dateFormat = 'LLL dd, y',
      disabled = false,
      fromDate,
      toDate,
      numberOfMonths = 2,
      className,
      variant = 'outline',
      align = 'start',
    },
    ref
  ) => {
    const t = useAppT()
    const [open, setOpen] = React.useState(false)

    const resolvedPlaceholder = placeholder ?? t('ui.datetime.pickDateRange')

    const formatRange = () => {
      if (!value?.from) return resolvedPlaceholder
      if (!value.to) return format(value.from, dateFormat)
      return `${format(value.from, dateFormat)} - ${format(value.to, dateFormat)}`
    }

    return (
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            ref={ref}
            variant={variant}
            disabled={disabled}
            className={cn(
              'w-full justify-start text-left font-normal',
              !value?.from && 'text-muted-foreground',
              className
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {formatRange()}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align={align}>
          <Calendar
            mode="range"
            selected={value}
            onSelect={onChange}
            disabled={disabled}
            fromDate={fromDate}
            toDate={toDate}
            numberOfMonths={numberOfMonths}
            initialFocus
          />
        </PopoverContent>
      </Popover>
    )
  }
)
DateRangePicker.displayName = 'DateRangePicker'

export { DatePicker, DateRangePicker }
