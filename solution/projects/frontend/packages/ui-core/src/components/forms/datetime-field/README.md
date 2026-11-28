# Date/time fields

`DateField` · `TimeField` · `DateTimeField` — native-engine, token-skinned
date/time inputs.

The browser's `<input type="date|time|datetime-local">` **is** the input engine:
segmented keyboard entry, locale-aware order, 12/24-hour by locale, arrow
increment, and the OS wheel on touch — all for free. This layer adds the
token-styled box, a leading icon, and (for date fields) a calendar popover for
mouse users. Values are ISO strings, so there's no timezone ambiguity at the
boundary.

| Component | `value` / `onChange` | Popover |
|---|---|---|
| `TimeField` | `"HH:mm"` (24h; `"HH:mm:ss"` when `step` < 60) | none — pure native segments |
| `DateField` | `"YYYY-MM-DD"` | `Calendar` (mouse; touch → OS wheel) |
| `DateTimeField` | `"YYYY-MM-DDTHH:mm"` | `Calendar` + a native `<input type="time">` |

## Props

**Shared:**

| Prop | Type | Notes |
|---|---|---|
| `value` / `defaultValue` | `string` | Controlled / uncontrolled (ISO, see table). |
| `onChange` | `(value: string) => void` | Emits the ISO string. |
| `disabled` | `boolean` | |
| `invalid` | `boolean` | Wires `aria-invalid` + destructive border. Usually driven by the `Field` / `Form` layer. |
| `min` / `max` | `string` | Native bounds, same ISO shape as the value. |
| `name` / `id` | `string` | The native input **is** the form control — no hidden-input shim. `id` lets an external `<label htmlFor>` bind to the real control. |
| `className` | `string` | Applied to the field shell. |
| `aria-label` | `string` | |

**`TimeField` only:** `step?: number` — native `step` in seconds (`60` → HH:mm;
smaller exposes a seconds segment; controls arrow increment).

**`DateField` / `DateTimeField` only:**

- `align?: 'start' | 'center' | 'end'` — popover alignment (default `'start'`,
  which keeps it under the field's left edge; Radix auto-flips on collision).
- `showPopover?: boolean` — default **AUTO**: shown on fine-pointer (mouse)
  devices, hidden on coarse-pointer (touch) ones, where tapping the field opens
  the OS date/time wheel — a better target than a mouse-first grid. Pass an
  explicit `true` / `false` to force it. (`DateField`'s popover is the calendar;
  `DateTimeField`'s is the calendar + a native time input.)

## Behaviour notes

- **AM/PM vs 24-hour is the browser's call**, from the user's OS locale. We never
  render our own time picker, so there's nothing to force or to desync. The wire
  value is always 24h `HH:mm`.
- **Calendar localization**: month/weekday names come from the app locale via
  `useLocaleOptional()` (`@djangocfg/i18n`) → date-fns locale. A bare calendar
  with no `I18nProvider` falls back to English.
- **Local-safe dates**: `date-time-utils.ts` parses/formats `YYYY-MM-DD`
  manually (not via `new Date(str)` / `toISOString()`), so the calendar day never
  shifts by timezone.
- **Popover fit**: `collisionPadding` keeps it off the viewport/modal edge; there
  is deliberately **no** `maxHeight` cap (that used the trigger-to-viewport gap
  and clipped the calendar when the field sat low) — Radix's default
  `avoidCollisions` flips the short popover above the field instead. A Popover
  inside a Dialog can additionally be handed a `collisionBoundary` by the caller.
- **Native chrome**: the browser's own clock/calendar glyph and spin buttons are
  suppressed via `.native-datetime-input` in
  `styles/css/utilities/datetime-field.css`; `.native-datetime-input--center`
  centers a value's segments cross-engine.

## Migration

The old click-only `TimePicker` / `DatePicker` stay exported as back-compat
aliases (zero consumer churn). Prefer these `*Field` components. `DateRangePicker`
is unchanged (still the react-day-picker range grid).

## Files

- `native-field-shell.tsx` — the shared token-styled box (surface, focus ring,
  icon slot, invalid/disabled).
- `date-field.tsx` / `time-field.tsx` / `date-time-field.tsx` — the three fields.
- `popover-chevron.tsx` — the leading `IconTrigger` + trailing `PopoverChevron`.
- `date-time-utils.ts` — local-safe ISO ↔ `Date` helpers.
