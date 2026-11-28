# ColorPalette

Grid of color swatches with copy-on-click. Source can be the active theme, a status preset family, or a custom list.

```tsx
import { ColorPalette } from '@djangocfg/ui-tools/color-palette';

// Render the current theme tokens
<ColorPalette mode="theme" columns={4} />

// Custom swatches
<ColorPalette
  mode="custom"
  colors={[{ name: 'Brand', value: '#0989aa' }]}
  copyFormat="hex"
/>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `mode` | `'theme' \| 'preset' \| 'custom'` | `'custom'` if `colors` provided, else `'theme'` | Where swatches come from. |
| `colors` | `ColorEntry[]` | — | Required when `mode === 'custom'`. |
| `columns` | `number` | `4` | Grid columns. |
| `copyFormat` | `'hex' \| 'rgb' \| 'hsl'` | `'hex'` | Format of the copied + rendered value. |
| `showName` | `boolean` | `true` | Show the color label. |
| `showValue` | `boolean` | `true` | Show the color value string. |

Storybook: `apps/storybook/stories/ui-tools/visual/ColorPalette.stories.tsx`

---

Adapted from jalcoui (MIT).
