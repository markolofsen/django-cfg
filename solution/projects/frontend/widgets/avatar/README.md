# @djangocfg/widget-avatar

A face derived from a seed, in a style the same seed chooses: **one seed → one
style → one face, forever, with nothing persisted.**

People draw from six character styles, places and tools from abstract ones, so a
mixed roster separates by **silhouette** before any glyph is read.

## Install

```bash
pnpm add @djangocfg/widget-avatar @djangocfg/ui-core
```

## Use

```tsx
import { SeededAvatar, roleAvatarSeed } from '@djangocfg/widget-avatar';

<SeededAvatar seed={roleAvatarSeed(user.id)} size={40} />
```

A server component renders through the server entry, which does not reach the
design system:

```tsx
import { ServerAvatar } from '@djangocfg/widget-avatar/server';
```

Let a user choose their own face with `FacePicker` (a client component — it is
why the server entry exists):

```tsx
import { FacePicker } from '@djangocfg/widget-avatar';

<FacePicker value={seed} onChange={setSeed} />
```

## Exports

| Subpath | Exports |
|---|---|
| `.` | `SeededAvatar`, `FacePicker`, `roleAvatarSeed`, `skillAvatarSeed`, `mcpAvatarSeed`, `AvatarKind` |
| `./server` | `ServerAvatar` + the same seed rules and corpora |

Both entries share the seed rules and the corpora, so the two paths draw the
same face — only the rendering strategy differs.

## Who seeds a face

Deciding *which* identity seeds a face is the host's job, not this package's.
Pass a stable string; the package turns it into a style and a drawing.

## Verify

```bash
pnpm --filter @djangocfg/widget-avatar check-types test
```
