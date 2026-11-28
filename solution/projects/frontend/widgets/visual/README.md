# @djangocfg/widget-visual

Presentation pieces: colour, motion, a code symbol, and two ways to show media
that are not a viewer.

## Install

```bash
pnpm add @djangocfg/widget-visual @djangocfg/ui-core @djangocfg/i18n
```

| Subpath | What |
|---|---|
| `./color-picker` | a colour picker |
| `./color-palette` | a palette built from one seed |
| `./marquee` | a continuous scroll |
| `./qr-code` | a QR code; the encoder is a dynamic import |
| `./gallery` | an image grid, carousel, thumbnails and lightbox |
| `./lottie-player` | a Lottie animation |

## What is NOT here

This is the residue of ui-tools' `visual/` and `media/` folders after the parts
with a real home left, and knowing where they went is half the package:

| Looking for | It is in |
|---|---|
| an image viewer with zoom and pan | `@djangocfg/widget-media` |
| an audio or video player | `@djangocfg/widget-player` |
| a chart or an indicator | `@djangocfg/widget-charts` |
| a dialog, tour or scroll spy | `@djangocfg/widget-overlay` |
| a file icon | `@djangocfg/widget-data` |

What remains genuinely belongs together: each puts something on screen for its
own sake, and none owns state a host has to drive.

## Verify

```bash
pnpm --filter @djangocfg/widget-visual check-types test
```
