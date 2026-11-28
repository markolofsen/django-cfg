# @djangocfg/widget-media

Media viewers for a conversation or a file preview: a zoom/pan image lightbox,
mermaid diagrams, markdown for a reader, and read-only code listings.

## Install

```bash
pnpm add @djangocfg/widget-media @djangocfg/ui-core streamdown
```

## Exports

**Each viewer is its own subpath, and that is the contract.** The root barrel
carries the image viewer only; the other three pull a parser or a highlighter,
and a host mounting a lightbox must not pay for any of them.

| Subpath | What it is | What it costs |
|---|---|---|
| `.` | `ImageLightbox`, `LazyImageLightbox`, `ImageViewer`, `LazyImageViewer`, hooks, types, constants | `yet-another-react-lightbox` (lightbox), `react-zoom-pan-pinch` (viewer) |
| `./diagram` | `LazyDiagram`, `DiagramSource`, `diagramPlugin` | mermaid (~2.5 MB) — **always deferred** |
| `./markdown` | `Markdown` — for a reader, outside any conversation | streamdown |
| `./code` | `Code` — a read-only listing | streamdown + shiki |
| `./i18n` | `MediaCopy`, `DEFAULT_MEDIA_COPY`, `MEDIA_DICTIONARIES`, `useMediaCopy` | — |

```tsx
import { ImageViewer } from '@djangocfg/widget-media';
import { LazyDiagram } from '@djangocfg/widget-media/diagram';

<ImageViewer images={[{ name: 'chart.png', src }]} lightbox />
<LazyDiagram chart={source} streaming={isStreaming} />
```

## Copy

The package owns its copy, typed, in the 17 `@djangocfg/i18n` locales. The
language comes from the `@djangocfg/i18n` provider (English without one). Pass
`copy` to override any subset; keys you omit keep the dictionary's text, so
changing one label does not blank the rest.

```tsx
<ImageViewer images={images} copy={{ zoomIn: 'Приблизить', close: 'Закрыть' }} />
```

`MediaCopy` is the schema of record — a misspelled key is a `tsc` error, not
`undefined` rendered into a toolbar button.

## Image lightbox

The modal gallery a click on a picture opens, on
[yet-another-react-lightbox](https://github.com/igordanchenko/yet-another-react-lightbox):
focus trap, swipe, preload of the neighbours, keyboard, wheel/pinch zoom,
thumbnails and a counter. Double-click zooms in at the pointer and the next one
zooms back out; the cursor is a magnifier at rest and a hand only while zoomed.
The skin is `src/image-viewer/lightbox/lightbox.css`: YARL's `--yarl__*`
variables mapped to ui-core tokens, so it follows light/dark and every preset.

```tsx
import { LazyImageLightbox } from '@djangocfg/widget-media';

<LazyImageLightbox
  images={[{ name: 'a.jpg', src, downloadSrc }]}
  open={index !== null}
  index={index ?? 0}
  onIndexChange={setIndex}
  onClose={() => setIndex(null)}
/>
```

It takes addresses (`LightboxImage`), never raw bytes; an in-memory image goes
through `ImageViewer`. `LazyImageLightbox` renders nothing until `open`.

## Image viewer

The embedded editor: zoom (wheel + presets 25/50/100/200/400%), pan by drag,
rotate 90°, flip H/V, fullscreen dialog, keyboard shortcuts (`+`/`-`, `0`
reset, `r` rotate), progressive loading with LQIP, checkerboard transparency
ground, cached dimension display. Double-click zooms to the pointer from fit and
back to fit from anywhere else. The `lightbox` prop is the older fullscreen
presentation, superseded by `ImageLightbox` and kept so existing hosts compile.

## Verify

```bash
pnpm --filter @djangocfg/widget-media check-types test
```
