# Theme & token troubleshooting

Symptom-first. Each entry: what you see → why → the fix.

The product palette is static CSS imported from `styles/presets/*`. The React
theme layer only changes `.dark`; if the palette is missing, inspect the CSS
import/export path before debugging React state or localStorage.

---

## "Random white borders + transparent fills on part of the page"

### What you see
- Some surfaces render with **no background** (`bg-muted` / `bg-card` / a custom
  `bg-bubble-*` come out transparent).
- Some borders render **bright white / light grey** instead of the hairline token
  — `border-border` looks white, but `border-divider` next to it looks correct.
- It only happens in **one region** of the page (often a marketing landing or a
  card), not the whole app. A sibling app/route with the same components is fine.

### Why (the actual mechanism)
A subtree is wrapped in **`<ForceTheme>`** (or any hand-written element that sets
token CSS vars inline) where a token is declared as a **bare HSL triplet**:

```css
--muted: 0 0% 10%;     /* ❌ */
--border: 0 0% 15%;    /* ❌ */
```

ui-core's utilities consume tokens **raw** (`@theme inline` maps
`--color-muted: var(--muted)`, and `.bg-muted { background-color: var(--muted) }`).
So `var(--muted)` resolves to the **string** `"0 0% 10%"`, which is not a valid
color → the browser **drops the declaration**:

- `background-color` drop → falls back to `transparent`.
- `border-color` drop → falls back to the inherited `currentColor` (≈ the light
  text color on a dark UI → "white border").

`border-divider` keeps working because that subtree doesn't *re-declare*
`--divider`, so it still inherits the valid preset value.

**This is NOT a Tailwind content-scan / `@source` problem.** The `.bg-muted`
rule exists in the built CSS; its *input variable* is the broken thing.

### How to confirm (60 seconds in the browser console)
```js
// 1) is the utility rule transparent on a real element?
getComputedStyle($0).backgroundColor          // rgba(0,0,0,0) on a bg-muted node = bug

// 2) is there a ForceTheme div with bare-triplet vars above it?
[...document.querySelectorAll('div[style*="--muted"]')]
  .map(d => d.style.getPropertyValue('--muted'))   // "0 0% 10%" (no hsl) = the culprit

// 3) sanity: a probe OUTSIDE the subtree works
const p = document.createElement('div'); p.className='bg-muted';
document.body.appendChild(p);
getComputedStyle(p).backgroundColor               // rgb(57,57,60) → proves the utility is fine
p.remove();
```
If (1) is transparent but (3) is a real color, the input var is broken, not the
utility — look up the tree for an inline token override.

### Fix (in order of preference)
1. **Stop forcing the theme with `ForceTheme`.** If the goal was just "this route
   is dark", drive it through the router with **`ThemeOverride`** in the app shell
   (`rules={[{ path: '/', theme: 'dark' }]}`) and delete the wrapper. The real
   preset tokens (already valid `hsl(...)`) cascade and the bug is gone. This is
   the right fix 90% of the time.
2. **If you genuinely need `ForceTheme`** (a subtree in the opposite theme), make
   sure every inline token value is a **full color**: `--muted: hsl(0 0% 10%)`,
   not `0 0% 10%`. ui-core's shipped `ForceTheme` already does this.
3. **Never** "fix" it by adding plain `.bg-x { background: var(--x) }` overrides in
   the app's `globals.css` — that masks the broken input and rots.

---

## "ALL utilities missing (only @theme vars load)" — a different bug

If `bg-*` / `border-*` are missing **everywhere** (not just one subtree) while the
`--token` variables are present, that IS a content-scan problem, not this one:
Tailwind v4 didn't scan your app source. See
[`../styles/README.md`](../styles/README.md) §"Why `@source` is required" — add
`@source "../../app"` (path relative to the CSS file) or check the app dir isn't
`.gitignore`d. Distinguish the two: **scan bug = global**, **token bug = one
subtree under an inline override.**

---

## "`hsl(var(--x))` shows the default / no color"

Tokens are already full colors. `hsl(hsl(0 0% 10%))` is invalid. Use
`var(--x)` directly, or `color-mix(in oklab, var(--x) N%, transparent)` for
opacity. See `styles/README.md` §"Token format".
