# Django-CFG Storybook

This app is the canonical package catalog, integration workbench, and executable
isolated-state specification for the Django-CFG frontend workspace.

## Commands

Run from `projects/solution/frontend`:

```bash
pnpm --filter @djangocfg/storybook dev
pnpm --filter @djangocfg/storybook check
pnpm --filter @djangocfg/storybook test:stories:contracts
pnpm --filter @djangocfg/storybook test:stories:watch
pnpm --filter @djangocfg/storybook test:stories:all
pnpm --filter @djangocfg/storybook build
```

`test:stories:contracts` is the fast pull-request gate. `test:stories:all` is a
diagnostic inventory and must not become blocking until its runtime and existing
debt are classified.

## Catalog grammar

Use package-oriented roots:

- `UI Core/<Category>/<Component>`
- `UI Tools/<Domain>/<Component>`
- `Layouts/<Component>`
- `Payments/<Component>`
- `Devtools/<Component>`
- `API Client/<Component>`
- `i18n/<Component>`
- `Next.js Utils/<Component>`

Do not add `(Docs)` suffixes or alternate casing such as `UI Tools/chat`.

## Story tags

- `contract`: deterministic, blocking render/interaction/accessibility case;
- implicit `test`: broad render inventory;
- `manual`: real permissions, persistence, media, or reviewer-led behavior;
- `experimental`: unstable API or unfinished fixture.

`manual` and `experimental` stories remain available through the sidebar filter
but are excluded from automated browser projects.

## Adding a contract

1. Choose one representative user outcome, not every visual variant.
2. Use a deterministic mock adapter/transport and user-facing accessible queries.
3. Add `tags: ['contract']` to the exact story, not necessarily its whole meta.
4. Set `parameters.a11y.test` to `error`. Use `todo` only on the exact story with
   a documented shared defect and owner.
5. Add the CSF file to `.storybook-contract/main.ts`. This explicit manifest is
   required because tag filtering does not prevent Storybook from transforming
   every indexed CSF file.
6. Keep network, cookies, routing, backend authentication, Stripe redirects,
   WebSockets, and browser permissions in real-application E2E.

## Lifecycle and persistence

The preview clears `localStorage` and `sessionStorage` before and after normal
stories and restores body styles. Stories whose public contract is persistence
must opt out explicitly:

```ts
parameters: {
  djangocfg: {
    storage: 'preserve',
  },
}
```

Persistence demonstrations should normally also carry the `manual` tag. Never
add a global console suppression or a catalog-wide axe rule disable.

## Installed app (PWA) review

**Device** (toolbar, global for every story of every package): `Off` (default: the story's own globals and the two
items below decide), `Browser phone`, `PWA phone` (standalone + iPhone island, top 59 / bottom 34) and `Auto (real)`
(nothing emulated). URL: `?sb-device=off|browser|pwa|auto` (wins over the toolbar), e.g.
`iframe.html?id=...&sb-device=pwa&globals=viewport.value:iphone14`. `?sb-emulate=1` still forces emulation on a
real touch device. The Device switch only sets display mode and insets; pick the phone width with the Viewport menu.

**Display mode** has three values: `Auto (real)` (default: nothing is touched), `Browser tab (emulated)` and
`Installed app (emulated)`. Emulation is applied only on a desktop-like environment. On a real touch device (coarse
pointer, touch points, phone-sized screen) it is ignored even if the URL carries `displayMode:standalone` or a
safe area: no overlay, no mocked `matchMedia`, no injected insets, so real `env()` and the real display mode apply and
you can add the Storybook page to the home screen to review true PWA behaviour. `?sb-emulate=1` forces emulation on a
device. The `... Drawer Open` stories open the drawer automatically (they wait for the trigger, click it once, wait
for the drawer); `...DrawerLongList` has many rows so the nav scrolls.

Toolbar items **Display mode** (Browser tab / Installed app) and **Safe area** (none / iPhone island 59+34 / iPhone SE 20)
emulate what Storybook cannot do natively: they wrap `matchMedia('(display-mode: ...)')` so `useIsPwa()` sees standalone,
set `<html data-display-mode>`, and set `--app-safe-*` (the `--safe-*` tokens read them before `env(...)`), drawing a
status bar / island / home-indicator overlay. Pick a phone from the viewport menu (iPhone 14, SE, 16 Pro, Pro Max).
Deep link: `?globals=displayMode:standalone;safeArea:iphone;viewport.value:iphone14`. Code:
`.storybook/preview/display-mode-switcher.tsx`. Stories: `Packages/Layouts/PrivateLayout` -> `PhoneBrowserDrawerOpen`,
`PhonePwaDrawerOpen`, `PhonePwaFullBleedTitleRow`, `PhonePwaPaddedPage`, `PhonePwaTopBarActions`.

Not testable here: double-tap zoom, pinch zoom, pull-to-refresh, iOS focus zoom and text selection are real-device
behaviours of an installed app. Use the "PWA behaviour checklist" page in the docs (`frontend/recipes`) on a real iPhone.

## Configuration map

- `.storybook/main.ts`: catalog, addons, sidebar filters, Vite policy;
- `.storybook/preview.tsx`: globals and composition only;
- `.storybook/config/docgen-policy.ts`: measured automatic-docgen decision;
- `.storybook/preview/`: theme/docs container, providers, frame, lifecycle;
- `.storybook-contract/`: small blocking transformation catalog;
- `vitest.config.ts`: Chromium contract and full-catalog projects.

The implementation plan and evidence live in
`../../@plans/plan-storybook-executable-library/`.
