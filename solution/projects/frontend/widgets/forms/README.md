# @djangocfg/widget-forms

Input surfaces: the things a user fills in, picks from, drags or speaks into.

Nine tools that share a job rather than a library — a form generated from a
schema, two upload surfaces, a cron builder, three interaction primitives, a
speech engine, and the registry that lets a voice button drive someone else's
composer.

## Install

```bash
pnpm add @djangocfg/widget-forms
```

Peers: `react` 19, `react-dom` 19, `@djangocfg/ui-core`, `@djangocfg/i18n`,
`lucide-react`, `zustand`.

## Import a subpath

There is no root barrel worth importing. `json-form` carries RJSF and its AJV
validator; `upload` carries Rpldy; `speech-recognition` carries a store and an
engine. None of them belongs in an app that wanted a combobox.

| Subpath | What it is |
|---|---|
| `./json-form` | `JsonSchemaForm`, lazy — a JSON Schema in, a themed form out |
| `./json-form/full` | the same, eager, for a surface that always shows one |
| `./upload` | `Uploader` — dropzone, previews, clipboard paste, abort |
| `./file-upload` | the single-file control, when a batch would be overkill |
| `./cron-scheduler` | `CronScheduler`, lazy — builds and explains a cron expression |
| `./combobox` | a composed combobox (`Trigger` / `Input` / `List` / `Item`) |
| `./sortable` | drag-to-reorder over dnd-kit |
| `./scroller` | a scroll container with the affordances a list needs |
| `./speech-recognition` | dictation, push-to-talk, engines, mic meter, language search |
| `./composer-registry` | the seam a voice button uses to type into a composer it does not own |
| `./sounds` | the short UI sounds the surfaces here play |

```tsx
import { JsonSchemaForm } from '@djangocfg/widget-forms/json-form';
import { Combobox, ComboboxInput, ComboboxList, ComboboxItem }
  from '@djangocfg/widget-forms/combobox';
```

## `composer-registry` is why speech and chat can stay apart

A dictation button must put text into a composer. If it imported one, this
package would depend on the chat surface — so instead a composer *registers* a
handle (`ComposerHandle`), and the voice widget looks one up. The producer side
is `@djangocfg/widget-chat` and any TipTap host; the consumer side is
`./speech-recognition`. Neither imports the other.

`ComposerHandle` is the one type the root barrel exports, because a host
implementing the producer side needs it without pulling a widget in.

## Testing

```bash
pnpm --filter @djangocfg/widget-forms check-types test
```

Six suites, all under `speech/` — the reducer, the transcript assembly, the id
generator, language matching and search, and the Web Speech engine. That is
where the logic is; the rest of this package is composition over `ui-core`.
