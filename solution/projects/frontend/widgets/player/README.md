# @djangocfg/widget-player

One media element that plays **both audio and video**, and the surfaces that
borrow it: a footer dock, a route stage, and a transcript row.

Replaces `@djangocfg/ui-tools`' separate `AudioPlayer` and `VideoPlayer`. Two
independent players are two owners of "what is playing", and that race is
*audible*.

## Install

```bash
pnpm add @djangocfg/widget-player @djangocfg/ui-core
```

## Layers

Each is importable alone, so a host mounting a transcript row does not pull the
dock.

| Subpath | What it is |
|---|---|
| `.` | everything below |
| `./element` | the ONE media element, and the failure translation |
| `./model` | pure projection — what a surface renders. No React. |
| `./surfaces` | `PlayerDock` (footer), `PlayerStage` (route), `MediaButton` (a row), `TrackCover`, `PlayerInfo` |
| `./domain` | `MediaTrack`, `MediaDetail`, `MediaFailure`, `machineTrack` — the product language |
| `./i18n` | 17 typed dictionaries; `PlayerCopy` is the schema of record |

## The seam

**This package does not import a store.** State arrives as props, intents leave
as callbacks — which is what lets every surface render in Storybook with no
store and no transport.

```tsx
import { PlayerDock, MediaButton, trackFromLink } from '@djangocfg/widget-player';

// A row in a transcript. Mounts nothing — for every kind, video included.
<MediaButton track={track} onPlay={play} />

// The footer dock HOLDS the element.
<PlayerDock track={track} playing={playing} onToggle={toggle} onOpenStage={open} />
```

Turning an address into a track needs two answers only a transport has — the
playable kind and the URL that plays — so the caller supplies them:

```tsx
const track = trackFromLink(hostId, path, {
  kind: 'audio',
  src: playableUrl,
  poster: coverUrl,   // optional; supplied, never derived
});
```

## Copy

The package owns its copy, typed. `usePlayerCopy()` reads the active locale from
`@djangocfg/i18n` when a provider is mounted and falls back to English when one
is not — so a surface renders in a test without standing up a provider.

## Verify

```bash
pnpm --filter @djangocfg/widget-player check-types test
```
