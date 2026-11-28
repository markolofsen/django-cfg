# Theme runtime

`@djangocfg/ui-core` separates static design tokens from runtime mode
selection:

- `@djangocfg/ui-core/styles/css/` owns all CSS tokens and presets.
- `ThemeProvider` owns the `html.dark` class and light/dark preference.
- `ThemeOverride` temporarily changes that class for a route.
- `ForceTheme` is only for a genuinely opposite-theme subtree.

Select a preset in the host stylesheet, after the golden-path styles:

```css
@import "@djangocfg/ui-core/styles/full";
@import "@djangocfg/ui-core/styles/presets/macos";
```

There is no runtime preset injection, token builder, or `ThemeStyleBridge`.
Navigation, hydration, lazy chunks, CDN revalidation, and system preference
changes cannot remove or replace the product palette.

## Exports

| Export | Responsibility |
|---|---|
| `ThemeProvider` / `useThemeContext` | `next-themes` wrapper; owns `.dark` and light/dark/system preference. |
| `ThemeToggle` | Light/dark toggle. |
| `ThemeSegmented` | Light/dark/system control. |
| `ThemeOverride` | Route-aware light/dark override using the real provider. |
| `resolveForcedTheme` | Pure route-rule matcher. |
| `ForcedThemeProvider` / `useForcedTheme` | Context for a currently forced mode. |
| `ForceTheme` | Last-resort scoped subtree override with valid full-color tokens. |

## Choosing a runtime mode

Use `ThemeOverride` when a complete route must be dark or light:

```tsx
<BaseApp theme={{ defaultTheme: 'dark' }}>
  <ThemeOverride pathname={pathname} rules={[{ path: '/', theme: 'dark' }]} />
  {children}
</BaseApp>
```

Use `ForceTheme` only when one subtree must differ from the surrounding page.
It is not a preset selector and does not replace the host CSS import.

## Token rule

Every color variable must be a complete CSS color:

```css
--muted: hsl(240 3% 11%); /* valid */
```

Never use a bare HSL triplet such as `240 3% 11%`; Tailwind consumes semantic
variables directly and the browser will drop invalid color declarations.
