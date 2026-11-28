"use client"

import * as React from 'react';

import { Combobox, type ComboboxOption } from './combobox';

/** Sentinel option value for "follow the browser" — never an IANA name. */
const AUTO = '__auto__';

export interface TimezoneSelectProps {
  /** IANA zone (e.g. `Europe/Madrid`); `null`/`undefined` = automatic (browser). */
  value?: string | null;
  onChange?: (timezone: string | null) => void;
  /** Offer the "Automatic" option. Default: true. */
  allowAuto?: boolean;
  /** Label of the automatic option (the detected zone is its description). */
  autoLabel?: string;
  placeholder?: string;
  searchPlaceholder?: string;
  emptyText?: string;
  className?: string;
  disabled?: boolean;
}

/** The browser's zone, or `UTC` where Intl cannot tell. */
export function detectTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  } catch {
    return 'UTC';
  }
}

/** Current offset of a zone as `UTC+01:00` (`UTC` for zero). */
export function timezoneOffsetLabel(timeZone: string, at: Date = new Date()): string {
  try {
    const part = new Intl.DateTimeFormat('en-US', { timeZone, timeZoneName: 'longOffset' })
      .formatToParts(at)
      .find((p) => p.type === 'timeZoneName')?.value;
    if (!part || part === 'GMT') return 'UTC';
    return part.replace('GMT', 'UTC');
  } catch {
    return 'UTC';
  }
}

/** Offset in minutes, for ordering. */
function offsetMinutes(label: string): number {
  const m = /UTC([+-])(\d{2}):(\d{2})/.exec(label);
  if (!m) return 0;
  return (m[1] === '-' ? -1 : 1) * (Number(m[2]) * 60 + Number(m[3]));
}

/** `America/Argentina/Buenos_Aires` → `Buenos Aires`. */
function cityOf(timeZone: string): string {
  return (timeZone.split('/').pop() ?? timeZone).replace(/_/g, ' ');
}

function listTimezones(): string[] {
  const supported = (Intl as { supportedValuesOf?: (key: string) => string[] }).supportedValuesOf;
  const zones = supported ? supported('timeZone') : [];
  // `UTC` is not always part of supportedValuesOf — keep it reachable.
  return zones.includes('UTC') ? zones : ['UTC', ...zones];
}

/**
 * Time zone picker — a thin layer over `Combobox`: options come from
 * `Intl.supportedValuesOf('timeZone')` (no data dependency), each shown as
 * city + region with its current UTC offset, ordered by offset.
 *
 * `value` is an IANA name or `null` for "Automatic" (browser zone), so the
 * caller can store `null` and keep following the device.
 *
 * @example
 * ```tsx
 * <TimezoneSelect value={tz} onChange={setTz} />
 * ```
 */
export function TimezoneSelect({
  value,
  onChange,
  allowAuto = true,
  autoLabel = 'Automatic',
  placeholder = 'Select time zone…',
  searchPlaceholder = 'Search city or offset…',
  emptyText = 'No time zones found',
  className,
  disabled,
}: TimezoneSelectProps) {
  const detected = React.useMemo(detectTimezone, []);

  const options = React.useMemo<ComboboxOption[]>(() => {
    const now = new Date();
    const zones = listTimezones()
      .map((tz) => ({ tz, offset: timezoneOffsetLabel(tz, now) }))
      .sort((a, b) => offsetMinutes(a.offset) - offsetMinutes(b.offset) || a.tz.localeCompare(b.tz))
      .map<ComboboxOption>(({ tz, offset }) => ({
        value: tz,
        label: cityOf(tz),
        description: tz.includes('/') ? tz.split('/')[0]! : undefined,
        badge: offset,
      }));
    return allowAuto
      ? [{ value: AUTO, label: autoLabel, description: detected, badge: timezoneOffsetLabel(detected, now) }, ...zones]
      : zones;
  }, [allowAuto, autoLabel, detected]);

  const filter = React.useCallback((o: ComboboxOption, search: string) => {
    const q = search.trim().toLowerCase();
    if (!q) return true;
    // `+9` must find `UTC+09:00`: compare offsets without prefix, leading zero and `:00`.
    const short = (v: string) => v.toLowerCase().replace(/utc/g, '').replace(/([+-])0/g, '$1').replace(/:00/g, '');
    const offset = typeof o.badge === 'string' ? o.badge : '';
    return (
      o.value.toLowerCase().replace(/_/g, ' ').includes(q) ||
      o.label.toLowerCase().includes(q) ||
      offset.toLowerCase().includes(q) ||
      short(offset).includes(short(q))
    );
  }, []);

  return (
    <Combobox
      options={options}
      value={value ?? (allowAuto ? AUTO : '')}
      onValueChange={(v) => onChange?.(v === AUTO || v === '' ? null : v)}
      placeholder={placeholder}
      searchPlaceholder={searchPlaceholder}
      emptyText={emptyText}
      className={className}
      disabled={disabled}
      filterFunction={filter}
      contentClassName="w-72"
      renderValue={(o) =>
        o ? (
          <span className="flex min-w-0 items-baseline gap-2">
            <span className="truncate">{o.value === AUTO ? `${o.label} · ${cityOf(detected)}` : o.label}</span>
            <span className="shrink-0 text-xs text-muted-foreground">{o.badge}</span>
          </span>
        ) : (
          <span className="text-muted-foreground">{placeholder}</span>
        )
      }
    />
  );
}
