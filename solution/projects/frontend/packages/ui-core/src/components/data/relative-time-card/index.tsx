"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../../../lib/utils";

const relativeTimeCardVariants = cva(
  "inline-flex items-center gap-2 rounded-md px-2.5 py-1 text-sm font-medium",
  {
    variants: {
      variant: {
        default: "bg-muted text-muted-foreground",
        subtle: "bg-transparent text-muted-foreground",
        outline: "border border-border text-foreground",
        accent: "bg-accent text-accent-foreground",
      },
      size: {
        default: "text-sm px-2.5 py-1",
        sm: "text-xs px-2 py-0.5",
        lg: "text-base px-3 py-1.5",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

interface RelativeTimeCardProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof relativeTimeCardVariants> {
  /** Date value — a `Date`, an ISO 8601 string, or a timestamp in milliseconds */
  date: DateInput;
  /**
   * @deprecated Ignored. Dates are parsed as ISO 8601; arbitrary input patterns
   * went away with moment. Kept so existing call sites still type-check.
   */
  inputFormat?: string;
  /** Display format: relative | auto | datetime | custom */
  format?: "relative" | "auto" | "datetime" | "custom";
  /** Output pattern for `format="custom"`. Supports `YYYY MM DD HH mm ss`. */
  outputFormat?: string;
  /** Update interval in ms for relative format. @default 60000 */
  updateInterval?: number;
  /** Text before the time */
  prefix?: string;
  /** Text after the time */
  suffix?: string;
  /** Locale for display. @default "en" */
  locale?: string;
  /** Use UTC for all calculations. @default true */
  utc?: boolean;
  /** IANA zone the wall-clock text is shown in (`useTimezone().timezone`). @default the browser zone */
  timeZone?: string;
}

/* Built on `Intl`, not moment.
 *
 * moment bundles 137 locale files and this module was the last thing importing
 * it here. Because the package entry is `export *` under a file-level
 * `'use client'`, that cost reached every consumer of the barrel, not just the
 * ones rendering a date: measured on the MLS Caribbean property pages
 * 2026-10-17, two 805 KB chunks on every listing, for a component those pages
 * never render.
 *
 * `Intl.RelativeTimeFormat` and `Intl.DateTimeFormat` are in every browser this
 * package targets, and they localise from the `locale` prop rather than from a
 * global `moment.locale()` call — which was shared mutable state, so two cards
 * with different locales fought over it.
 *
 * Two deliberate narrowings, both of moment-only behaviour:
 *   - `inputFormat` no longer parses arbitrary patterns. `Date` accepts ISO
 *     8601; anything else was already locale-dependent guesswork.
 *   - `outputFormat` accepts the moment-style tokens this component actually
 *     shipped with (`YYYY MM DD HH mm ss`), not the full moment grammar.
 */

type DateInput = Date | string | number;

/** A timestamp with no zone designator is UTC here, as the APIs emit it. */
function toDate(value: DateInput, useUtc: boolean): Date {
  if (value instanceof Date) return value;
  if (typeof value === "number") return new Date(value);
  if (typeof value === "string") {
    const iso =
      useUtc && !/(?:Z|[+-]\d{2}:?\d{2})$/.test(value) ? `${value}Z` : value;
    return new Date(iso);
  }
  return new Date();
}

const RELATIVE_UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["year", 365 * 24 * 60 * 60],
  ["month", 30 * 24 * 60 * 60],
  ["day", 24 * 60 * 60],
  ["hour", 60 * 60],
  ["minute", 60],
  ["second", 1],
];

function getRelativeTime(date: Date, locale: string = "en"): string {
  const seconds = Math.round((date.getTime() - Date.now()) / 1000);
  const absolute = Math.abs(seconds);
  const formatter = new Intl.RelativeTimeFormat(locale, { numeric: "auto" });

  for (const [unit, size] of RELATIVE_UNITS) {
    if (absolute >= size || unit === "second") {
      return formatter.format(Math.round(seconds / size), unit);
    }
  }
  return formatter.format(0, "second");
}

function getAutoFormat(date: Date, locale: string = "en", timeZone?: string): string {
  const diffHours = (Date.now() - date.getTime()) / 3_600_000;
  const diffDays = diffHours / 24;

  if (diffHours < 24) {
    return new Intl.DateTimeFormat(locale, {
    timeZone,
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(date);
  }
  if (diffDays < 7) {
    return new Intl.DateTimeFormat(locale, {
    timeZone, weekday: "short" }).format(date);
  }
  if (diffDays < 365) {
    return new Intl.DateTimeFormat(locale, {
    timeZone,
      month: "short",
      day: "numeric",
    }).format(date);
  }
  return new Intl.DateTimeFormat(locale, {
    timeZone,
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
}

function getDateTimeFormat(date: Date, locale: string = "en", timeZone?: string): string {
  return new Intl.DateTimeFormat(locale, {
    timeZone,
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date);
}

/** The moment-style tokens this component shipped with, and only those. */
function applyCustomFormat(date: Date, pattern: string, timeZone?: string): string {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  }).formatToParts(date);
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? "";
  const tokens: Record<string, string> = {
    YYYY: get("year"),
    MM: get("month"),
    DD: get("day"),
    HH: get("hour"),
    mm: get("minute"),
    ss: get("second"),
  };
  return pattern.replace(/YYYY|MM|DD|HH|mm|ss/g, (t) => tokens[t] ?? t);
}

function formatDate(
  date: Date,
  format: "relative" | "auto" | "datetime" | "custom",
  locale: string,
  outputFormat?: string,
  timeZone?: string
): string {
  switch (format) {
    case "relative":
      return getRelativeTime(date, locale);
    case "auto":
      return getAutoFormat(date, locale, timeZone);
    case "datetime":
      return getDateTimeFormat(date, locale, timeZone);
    case "custom":
      return applyCustomFormat(date, outputFormat || "YYYY-MM-DD HH:mm", timeZone);
  }
}

const RelativeTimeCard = React.forwardRef<
  HTMLTimeElement,
  RelativeTimeCardProps
>(
  (
    {
      date,
      inputFormat,
      format = "relative",
      outputFormat,
      updateInterval = 60000,
      prefix,
      suffix,
      locale = "en",
      utc = true,
      timeZone,
      className,
      variant,
      size,
      ...props
    },
    ref
  ) => {
    const dateObj = React.useMemo(() => toDate(date, utc), [date, utc]);

    const [display, setDisplay] = React.useState(() =>
      formatDate(dateObj, format, locale, outputFormat, timeZone)
    );

    React.useEffect(() => {
      setDisplay(formatDate(dateObj, format, locale, outputFormat, timeZone));
      if (format !== "relative") return;
      const id = setInterval(() => {
        setDisplay(formatDate(dateObj, format, locale, outputFormat, timeZone));
      }, updateInterval);
      return () => clearInterval(id);
    }, [dateObj, format, locale, outputFormat, timeZone, updateInterval]);

    // An invalid date would throw from `toISOString`, where moment returned
    // null and rendered "Invalid date". Both attributes are omitted instead.
    const valid = !Number.isNaN(dateObj.getTime());
    const isoString = valid ? dateObj.toISOString() : undefined;
    const title = valid
      ? new Intl.DateTimeFormat(locale, {
          timeZone,
          dateStyle: "full",
          timeStyle: "short",
        }).format(dateObj)
      : undefined;

    return (
      <time
        ref={ref}
        dateTime={isoString}
        className={cn(relativeTimeCardVariants({ variant, size }), className)}
        title={title}
        {...props}
      >
        {prefix}
        {display}
        {suffix}
      </time>
    );
  }
);
RelativeTimeCard.displayName = "RelativeTimeCard";

export { RelativeTimeCard, relativeTimeCardVariants };
export type { RelativeTimeCardProps };
