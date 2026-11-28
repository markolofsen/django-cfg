# CronScheduler

Cron expression builder + read-only preview. Standard Unix 5-field format (`minute hour day-of-month month day-of-week`). Two surfaces:

- `<CronScheduler>` — interactive builder (daily / weekly / monthly / custom), popover or `inline`.
- `<CronPreview>` — standalone read-only summary with human description and next run times.

```tsx
import { CronScheduler, CronPreview } from '@djangocfg/ui-tools/cron-scheduler';

// Edit
<CronScheduler value={cron} onChange={setCron} showCronExpression />

// Display
<CronPreview value="0 9 * * 1-5" nextRuns={5} />
```

## `<CronScheduler>` props

| Prop | Type | Default | Description |
|---|---|---|---|
| `value` | `string` | — | Current cron expression. |
| `onChange` | `(cron: string) => void` | — | Fires on every valid state change. |
| `defaultType` | `'daily' \| 'weekly' \| 'monthly' \| 'custom'` | `'daily'` | Initial mode. |
| `showCronExpression` | `boolean` | `false` | Render the raw expression under the trigger. |
| `allowCopy` | `boolean` | `false` | Copy-to-clipboard button. |
| `timeFormat` | `'12h' \| '24h'` | `'24h'` | Time picker format. |
| `inline` | `boolean` | `false` | Expand the editor in place instead of a popover. |
| `size` | `'default' \| 'sm'` | `'default'` | Compact fields (`sm`) for narrow side panels / modals. |
| `placeholder` | `string` | — | Trigger label when no schedule is set (popover mode). |
| `disabled` | `boolean` | `false` | Disable all interactions. |

## `<CronPreview>` props

| Prop | Type | Default | Description |
|---|---|---|---|
| `value` | `string` | — | Cron expression to preview. Invalid values render a destructive-toned error card. |
| `title` | `string` | — | Optional heading above the summary. |
| `nextRuns` | `number` | `5` | Upcoming runs to list. `0` hides the list. |
| `showExpression` | `boolean` | `true` | Show the raw cron string alongside the summary. |
| `referenceDate` | `Date` | `new Date()` | Anchor for `getNextRuns`. |

## Utilities

Exported alongside the components for custom UIs:

- `buildCron(state)` / `parseCron(expr)` — state ↔ expression
- `isValidCron(expr)` — boolean validator
- `humanizeCron(expr)` — human-readable summary string
- `getNextRuns(expr, n, from?)` / `formatNextRun(date)` — upcoming run times

Advanced compositions can use `CronSchedulerProvider` + the slice hooks (`useCronType`, `useCronTime`, `useCronWeekDays`, `useCronMonthDays`, `useCronCustom`, `useCronPreview`, `useCronSize`) and field components (`ScheduleTypeSelector`, `TimeSelector`, `DayChips`, `MonthDayGrid`, `CustomInput`, `SchedulePreview`).

## Notes

- Builder is lazy-loaded (~15KB). `CronPreview` is not lazy — it ships with the entry module.
- `SchedulePreview` (inside the editor) and `CronPreview` (standalone) are distinct: the former reads from `CronSchedulerProvider`, the latter takes a value prop and stands alone.

---

Adapted from jalcoui (MIT).
