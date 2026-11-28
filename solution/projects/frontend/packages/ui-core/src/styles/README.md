# ui-core styles

CSS is the single source of truth for colors, typography, radius, status
surfaces, charts, and sidebar tokens. There are no TypeScript color maps and no
runtime token generator — do not add either.

## Layout

```text
styles/
├── css/
│   ├── full.css        # THE entry: Tailwind + tokens + base + utilities
│   ├── base.css        # resets
│   ├── sources.css     # Tailwind @source directives
│   ├── theme/          # tokens.css (the @theme map), light.css, dark.css
│   ├── utilities/      # focused utility modules
│   └── presets/        # the authoritative token values, one file per preset
├── palette/            # runtime readers of computed CSS variables
└── presets/            # TypeScript names and ordering only — never values
```

`index.css` and `globals.css` are compatibility entries. New consumers import
`full.css`.

## Consumer setup

```css
@import "@djangocfg/ui-core/styles/full";
@plugin "tailwindcss-animate";
@import "@djangocfg/ui-core/styles/presets/macos";
@import "@djangocfg/ui-tools/styles";
```

Order is load-bearing: the preset must come after `full.css` so its `:root` and
`.dark` values win. Application overrides come last.

`full.css` already imports Tailwind, tokens, base and utilities — a second
`@import "tailwindcss"` or `base.css` in the consumer is a duplicate. The
`tailwindcss-animate` plugin is registered by the consumer, not the package.

A preset defines both `:root` (light) and `.dark`. `ThemeProvider` only toggles
the `html.dark` class.

For a product adjustment, override after the preset:

```css
:root, .dark { --font-size-base: 0.9375rem; }
```

Do not build tokens at startup, append a `<style>` tag, or copy values into a
`theme-preset.ts`.

### Tailwind source scanning

`css/sources.css` must scan the package root from its own location:

```css
@source "../../**/*.{ts,tsx}";
```

Scanning `../` instead reaches only `src/styles` and silently drops every
utility used by components, `bg-overlay` among them. Consumers may add their own
`@source` lines but must not replace this one.

## Token format

Color variables are complete CSS colors, never bare HSL triplets. Use
`var(--background)` or `bg-background`; never `hsl(var(--background))`.

```css
:root { --background: hsl(240 17% 97%); }
.dark { --background: hsl(240 5% 8%); }
```

Typography variables are ordinary CSS values (`--font-size-base: 0.8125rem`).

### Raised and recessed surfaces

| Token | Reads as | Use for |
|---|---|---|
| `--surface-hover` | a step toward the reader | pointer feedback on a resting surface |
| `--surface-recessed` | sunk below the page | chrome framing content: a tab strip, a rail, a footer band |

`--surface-recessed` is a translucent black, not a mix with `--background`. A
percentage mix takes its step from what is already there, and a dark page has
almost nothing to take: 6% black into `hsl(240 5% 8%)` moved it two bytes out of
255, which no eye resolves. A fixed overlay steps by the same amount whatever
the page — and the alpha differs per theme, because the same overlay costs far
more contrast on a near-white ground.

**Never recess with `--muted` or `--card`.** Their direction is not guaranteed:
`theme/dark.css` keeps `--muted` below `--background`, while the macOS preset
raises every resting surface (background 8%, muted 11%, card 12%). A tab strip
painted `bg-muted` floated toward the reader on that preset and looked correct
in the base theme.

### Overlays and glass

`bg-overlay` takes its color from `--overlay` and its frosting from
`--overlay-blur` (default `5px`). A glass surface needs a translucent
background — an opaque `bg-card` makes the blur invisible.

An element inside an ancestor that already has `backdrop-filter` cannot blur the
page behind that ancestor: the ancestor becomes a backdrop root. Render such
surfaces through a body portal, positioned from their trigger.

`--overlay` is a modal BACKDROP — the wash between a dialog and the page. It is
not the colour of text laid over a photograph.

### Text over a consumer's image

There is **no token for this, deliberately.** Every semantic pair answers "what
colour is text on OUR surface", and a photograph is not one: it is arbitrary
content the consumer supplies, kept legible by a scrim the component paints.
`--foreground` over a darkened photo inverts to near-black in light mode and
disappears into the picture.

So a component rendering over media fixes a literal light colour and pairs it
with a scrim it controls — `AuthLayout`'s `.auth-brand-panel` is the worked
example. This is the "branded assets or an explicitly documented case" escape
in the rule above; keep the literal next to the comment that explains it, and
do not invent a `--on-media` token for one component.

## Preset rules

- Values live in `styles/css/presets/*.css`. `styles/presets/*.ts` holds names
  and ordering only.
- Every value must be a complete CSS color. Keep a preset's light and dark pairs
  in one file. A preset may omit tokens that inherit from `theme.css`.
- **Light mode:** `--muted` at least 2 lightness points darker than
  `--background`, so translucent muted fills stay visible.
- **Both modes:** an interactive surface sits at least 4 lightness points from
  the surface it lands on — `--accent` vs `--background`, `--sidebar-accent` vs
  `--sidebar-background`.

  Direction is not asserted, only the step size. The second pair exists because
  the first was not enough: a sidebar hover lands on `--sidebar-background`,
  which nothing checked, so presets shipped one-point steps in light against
  eleven in dark, and one hover came out lighter than the rail it highlighted —
  all while passing the `--muted` gate. **Check the surface the user sees, not a
  neighbour that happens to be nearby.**

  Because direction is free, product code must not infer it from a token's
  value. That is what `--surface-recessed` and `--surface-hover` are for.
- Density overrides belong in the consuming app's CSS.

## Verification

```bash
pnpm check:contrast   # preset gates + the macOS AA compact-text audit
pnpm check            # tsc --noEmit
```

`check:contrast` merges each static preset over the base theme, enforces the
rules above, and requires WCAG AA 4.5:1 for semantic pairs in both modes. When
tuning a token, move the semantic pair together rather than overriding text in a
consumer component.

Then build a consumer and look at both modes.

## Cross-repository changes

```bash
pnpm sync:cfg:one ui-core
pnpm sync:cfg:one i18n     # required peer when ui-core is synced locally
```

Restart the consumer's dev server afterward.

A sync is local and temporary: a clean install restores the published package,
so a source change survives only once a new version is published. Update the
dependency range with pnpm and let the lockfile record the resolution — never
delete `pnpm-lock.yaml` to force an update.
