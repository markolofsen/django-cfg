# BalancedText

Deterministic line-balancing for headings and short paragraphs. Wraps `@chenglou/pretext`'s `useBalancedWidth` to compute the narrowest container width that preserves the natural line count (or `maxLines`).

CSS `text-wrap: balance` is used as the SSR fallback — the balanced width takes over after mount.

```tsx
import { BalancedText } from '@djangocfg/ui-core';

<BalancedText as="h1" maxLines={2}>
  A balanced heading that never produces an orphan word
</BalancedText>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `children` | `string` | — | Text to balance. **Must be a plain string** — pretext measures glyphs, not React trees. |
| `font` | `string` | computed style | CSS font shorthand for measurement (e.g. `'16px Inter, sans-serif'`). |
| `maxWidth` | `number` | parent `clientWidth` or `600` | Hard cap on container width in px. |
| `maxLines` | `number` | — | Cap on rendered lines. Forces the narrowest width that keeps line count ≤ `maxLines`. |
| `as` | `ElementType` | `'span'` | Element to render as. |

Storybook: `apps/storybook/stories/ui-core/data/BalancedText.stories.tsx`

---

Adapted from jalcoui (MIT). Powered by [`@chenglou/pretext`](https://github.com/chenglou/pretext) (optional peer dependency).
