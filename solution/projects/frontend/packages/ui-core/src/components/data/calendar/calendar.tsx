"use client"

import { enUS, ko, ru, type Locale } from 'date-fns/locale';
import { ChevronDownIcon, ChevronLeftIcon, ChevronRightIcon } from 'lucide-react';
import * as React from 'react';
import { DayButton, DayPicker, getDefaultClassNames, type Matcher } from 'react-day-picker';

import { useLocaleOptional } from '@djangocfg/i18n';
import { cn } from '../../../lib/utils';
import { Button, buttonVariants } from '../../forms/button';

/** App locale code → date-fns Locale for react-day-picker (month/weekday
 *  names). `useLocaleOptional` returns null with no I18nProvider, so the
 *  calendar still works standalone (falls back to English). */
const DATE_FNS_LOCALES: Record<string, Locale> = { en: enUS, ru, ko };

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  captionLayout = "label",
  buttonVariant = "ghost",
  formatters,
  components,
  locale,
  fromDate,
  toDate,
  initialFocus,
  disabled,
  ...props
}: React.ComponentProps<typeof DayPicker> & {
  buttonVariant?: React.ComponentProps<typeof Button>["variant"]
  /** react-day-picker 9 name, kept for our callers: earliest selectable day. */
  fromDate?: Date
  /** react-day-picker 9 name, kept for our callers: latest selectable day. */
  toDate?: Date
  /** react-day-picker 9 name for `autoFocus`. */
  initialFocus?: boolean
}) {
  // react-day-picker 10 dropped fromDate/toDate/initialFocus. Map them onto the
  // v10 API: navigation bounds + disabled matchers + autoFocus.
  const limits: Matcher[] = []
  if (fromDate) limits.push({ before: fromDate })
  if (toDate) limits.push({ after: toDate })
  const mergedDisabled: Matcher | Matcher[] | undefined =
    limits.length === 0
      ? disabled
      : disabled === undefined || disabled === false
        ? limits
        : [...(Array.isArray(disabled) ? disabled : [disabled]), ...limits]

  const defaultClassNames = getDefaultClassNames()

  // Localize month/weekday names from the app locale. An explicit `locale` prop
  // still wins (the caller can override), and a bare calendar with no provider
  // falls back to English.
  const appLocale = useLocaleOptional()
  const resolvedLocale = locale ?? (appLocale ? DATE_FNS_LOCALES[appLocale] : undefined)

  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      locale={resolvedLocale}
      // Cell size: compact by default (fits a narrow popover); roomier on ≥sm
      // so the desktop popover isn't cramped.
      className={cn(
        "bg-background group/calendar p-3 [--cell-size:1.75rem] sm:[--cell-size:2.25rem] [[data-slot=card-content]_&]:bg-transparent [[data-slot=popover-content]_&]:bg-transparent",
        String.raw`rtl:**:[.rdp-button\_next>svg]:rotate-180`,
        String.raw`rtl:**:[.rdp-button\_previous>svg]:rotate-180`,
        className
      )}
      captionLayout={captionLayout}
      disabled={mergedDisabled}
      startMonth={fromDate}
      endMonth={toDate}
      autoFocus={initialFocus}
      formatters={{
        formatMonthDropdown: (date) =>
          date.toLocaleString("default", { month: "short" }),
        ...formatters,
      }}
      classNames={{
        root: cn("w-fit", defaultClassNames.root),
        months: cn(
          "relative flex flex-col gap-4 md:flex-row",
          defaultClassNames.months
        ),
        month: cn("flex w-full min-w-[calc(var(--cell-size)*7)] flex-col gap-4", defaultClassNames.month),
        nav: cn(
          "absolute inset-x-0 top-0 flex w-full items-center justify-between gap-1",
          defaultClassNames.nav
        ),
        button_previous: cn(
          buttonVariants({ variant: buttonVariant }),
          "h-(--cell-size) w-(--cell-size) select-none p-0 aria-disabled:opacity-50",
          defaultClassNames.button_previous
        ),
        button_next: cn(
          buttonVariants({ variant: buttonVariant }),
          "h-(--cell-size) w-(--cell-size) select-none p-0 aria-disabled:opacity-50",
          defaultClassNames.button_next
        ),
        month_caption: cn(
          "flex h-(--cell-size) w-full items-center justify-center px-(--cell-size)",
          defaultClassNames.month_caption
        ),
        dropdowns: cn(
          "flex h-(--cell-size) w-full items-center justify-center gap-1.5 text-sm font-medium",
          defaultClassNames.dropdowns
        ),
        dropdown_root: cn(
          "has-focus:border-ring border-border shadow-xs has-focus:ring-ring has-focus:ring-1 relative rounded-[var(--radius)] border",
          defaultClassNames.dropdown_root
        ),
        dropdown: cn(
          "bg-popover absolute inset-0 opacity-0",
          defaultClassNames.dropdown
        ),
        caption_label: cn(
          "select-none font-medium",
          captionLayout === "label"
            ? "text-sm"
            : "[&>svg]:text-muted-foreground flex h-8 items-center gap-1 rounded-md pl-2 pr-1 text-sm [&>svg]:size-3.5",
          defaultClassNames.caption_label
        ),
        month_grid: cn("w-full border-collapse", defaultClassNames.month_grid),
        weekdays: cn("flex", defaultClassNames.weekdays),
        weekday: cn(
          "text-muted-foreground flex-1 select-none rounded-md text-[0.8rem] font-normal",
          defaultClassNames.weekday
        ),
        week: cn("mt-2 flex w-full", defaultClassNames.week),
        week_number_header: cn(
          "w-(--cell-size) select-none",
          defaultClassNames.week_number_header
        ),
        week_number: cn(
          "text-muted-foreground select-none text-[0.8rem]",
          defaultClassNames.week_number
        ),
        day: cn(
          // Range end-caps use `rounded-lg` to MATCH the single-day / today
          // radius (`rounded-lg` on the button). Previously these were
          // `rounded-l-md`/`rounded-r-md`, which stamped a 6px radius onto just
          // the left OR right corners of a cell — so today/selected days at a
          // row edge came out asymmetric (sharp one side, round the other).
          "group/day relative aspect-square h-full w-full select-none p-0 text-center [&:first-child[data-selected=true]_button]:rounded-l-lg [&:last-child[data-selected=true]_button]:rounded-r-lg",
          defaultClassNames.day
        ),
        range_start: cn(
          "bg-accent rounded-l-lg",
          defaultClassNames.range_start
        ),
        range_middle: cn("rounded-none", defaultClassNames.range_middle),
        range_end: cn("bg-accent rounded-r-lg", defaultClassNames.range_end),
        today: cn(
          // "Today" ring only when NOT the selected day — otherwise the accent
          // panel bled out behind the primary selection and `rounded-none`
          // squared off one cell, so a selected "today" looked lop-sided vs
          // other selected days. When selected, the selection styles own the
          // cell entirely (full `rounded-md`, primary fill).
          "rounded-lg data-[selected=true]:bg-transparent data-[selected=true]:text-inherit data-[selected=false]:bg-accent data-[selected=false]:text-accent-foreground",
          defaultClassNames.today
        ),
        outside: cn(
          "text-muted-foreground aria-selected:text-muted-foreground",
          defaultClassNames.outside
        ),
        disabled: cn(
          "text-muted-foreground opacity-50",
          defaultClassNames.disabled
        ),
        hidden: cn("invisible", defaultClassNames.hidden),
        ...classNames,
      }}
      components={{
        Root: ({ className, rootRef, ...props }) => {
          return (
            <div
              data-slot="calendar"
              ref={rootRef}
              className={cn(className)}
              {...props}
            />
          )
        },
        Chevron: ({ className, orientation, ...props }) => {
          if (orientation === "left") {
            return (
              <ChevronLeftIcon className={cn("size-4", className)} {...props} />
            )
          }

          if (orientation === "right") {
            return (
              <ChevronRightIcon
                className={cn("size-4", className)}
                {...props}
              />
            )
          }

          return (
            <ChevronDownIcon className={cn("size-4", className)} {...props} />
          )
        },
        DayButton: CalendarDayButton,
        WeekNumber: ({ children, ...props }) => {
          return (
            <td {...props}>
              <div className="flex size-(--cell-size) items-center justify-center text-center">
                {children}
              </div>
            </td>
          )
        },
        ...components,
      }}
      {...props}
    />
  )
}

function CalendarDayButton({
  className,
  day,
  modifiers,
  ...props
}: React.ComponentProps<typeof DayButton>) {
  const defaultClassNames = getDefaultClassNames()

  const ref = React.useRef<HTMLButtonElement>(null)
  React.useEffect(() => {
    if (modifiers.focused) ref.current?.focus()
  }, [modifiers.focused])

  return (
    <Button
      ref={ref}
      variant="ghost"
      size="icon"
      data-day={day.date.toLocaleDateString()}
      data-selected-single={
        modifiers.selected &&
        !modifiers.range_start &&
        !modifiers.range_end &&
        !modifiers.range_middle
      }
      data-range-start={modifiers.range_start}
      data-range-end={modifiers.range_end}
      data-range-middle={modifiers.range_middle}
      className={cn(
        "data-[selected-single=true]:bg-primary data-[selected-single=true]:text-primary-foreground data-[range-middle=true]:bg-accent data-[range-middle=true]:text-accent-foreground data-[range-start=true]:bg-primary data-[range-start=true]:text-primary-foreground data-[range-end=true]:bg-primary data-[range-end=true]:text-primary-foreground group-data-[focused=true]/day:border-ring group-data-[focused=true]/day:ring-ring",
        // Centered content + a radius that scales with the (now larger) cell so
        // the selected day reads as a rounded square, not a hard box.
        "flex aspect-square h-auto w-full min-w-(--cell-size) flex-col items-center justify-center gap-1 rounded-lg font-normal leading-none",
        "data-[range-end=true]:rounded-lg data-[range-middle=true]:rounded-none data-[range-start=true]:rounded-lg",
        "group-data-[focused=true]/day:relative group-data-[focused=true]/day:z-10 group-data-[focused=true]/day:ring-1 [&>span]:text-xs [&>span]:opacity-70",
        defaultClassNames.day,
        className
      )}
      {...props}
    />
  )
}

export { Calendar, CalendarDayButton }
