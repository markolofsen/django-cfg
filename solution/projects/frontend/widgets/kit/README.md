# @djangocfg/widget-kit

Shared ground for the djangocfg widgets: what more than one surface has to
agree on, and nothing else.

**A widget may depend on this. This depends on no widget.**

## What is here

| Subpath | Exports |
|---|---|
| `.` / `./format` | `formatBytes`, `formatClock`; `normalize`, `basename`, `extension`, `dirname`, `segments`, `isAbsolute`, `unquote`, `elidePath`, `elideName`, `elidePathLine` |
| `./pretty-code` | `PrettyCode` (Prism listing: header, copy, wrap, light/dark, compact, `pending`), `CodePanelHeader`, `languageLabel`, `normalizePrismLanguage`, `ensurePrismLanguages`, `useEnsurePrismLanguages` |
| `./pretty-code/lazy` | `LazyPrettyCode`, the same component behind a lazy boundary |
| `./lazy` | `createLazyComponent`, `LazyWrapper`, `Spinner`, and the placeholders `LoadingFallback`, `InlineLoadingFallback`, `CardLoadingFallback`, `MapLoadingFallback`; `configureLazyCopy` |

**`./lazy` is not re-exported from the root**, and that is the one deliberate
exclusion: it is React and pulls `@djangocfg/ui-core` behind it, while the root
is pure. A consumer wanting `formatBytes` must not pay for a component tree.

```ts
import { formatBytes, formatClock, elidePathLine } from '@djangocfg/widget-kit';

formatBytes(1536);                       // '1.5 KB'   — binary steps
formatClock(214);                        // '3:34'     — a track, not a duration
elidePathLine('/very/long/path.txt', 24) // '…/path.txt'
```

## Placeholders

```tsx
import { createLazyComponent, MapLoadingFallback } from '@djangocfg/widget-kit/lazy';

export const LazyMap = createLazyComponent(
  () => import('./MapContainer').then((m) => ({ default: m.MapContainer })),
  { displayName: 'LazyMap', fallback: <MapLoadingFallback minHeight={400} /> },
);
```

Copy is a typed object resolving to English, not a `t(key)` lookup: a
placeholder renders in stories, tests and server passes — the three places
least likely to have mounted a provider. Replace it once at startup with
`configureLazyCopy({ loading: '…' })`.

## The entry price

**Nothing lands here on the strength of looking reusable — a second consumer is
the entry price.** A one-consumer helper in a shared package is a helper in the
wrong package: it is now a public API, it constrains the widget that owns it,
and nobody can change it without checking a caller that does not exist.

The point of the package is the opposite property: the same byte count must not
format differently across two surfaces.

## Verify

```bash
pnpm --filter @djangocfg/widget-kit check-types test
```
