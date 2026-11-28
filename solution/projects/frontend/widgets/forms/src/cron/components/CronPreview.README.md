# CronPreview

Read-only companion to `CronScheduler`. Renders a human-readable summary of a cron expression and an optional list of upcoming run times. Standalone — no `CronSchedulerProvider` required.

Use it in dashboards, list rows, and read-only schedule views.

```tsx
import { CronPreview } from '@djangocfg/ui-tools/cron-scheduler';

<CronPreview value="0 9 * * 1-5" />
<CronPreview value="*/15 * * * *" nextRuns={5} />
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `value` | `string` | — | Standard 5-field cron expression. |
| `title` | `string` | — | Optional heading above the summary. |
| `nextRuns` | `number` | `5` | Upcoming run times to display. `0` hides the list. |
| `showExpression` | `boolean` | `true` | Show the raw cron expression alongside the summary. |
| `referenceDate` | `Date` | `new Date()` | Base date for computing next runs. |

Storybook: `apps/storybook/stories/ui-tools/cron/CronPreview.stories.tsx`

---

Adapted from jalcoui (MIT).
