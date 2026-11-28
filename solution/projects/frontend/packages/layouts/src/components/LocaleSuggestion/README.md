# LocaleSuggestion

The "This page is available in Deutsch" hint. `BaseApp` mounts it; an app that already passes `i18n` has nothing to do.

```tsx
<BaseApp i18n={{ locale, locales, onLocaleChange, routing }}>   {/* hint is on */}
<BaseApp i18n={{ ..., suggestion: false }}>                      {/* off */}
<BaseApp i18n={{ ..., suggestion: { exclude: [/^\/[a-z]{2}\/legal/], delayMs: 2000, ttlDays: 90 } }}>
```

## When it shows

The first browser language (`navigator.languages`, in order) that the site speaks decides. It is offered only if that
language is not the page's own. `de-AT` offers `de`; `pt` offers `pt-BR`; `en-GB` on `en` says nothing; a language the
site lacks says nothing (no nearest guess). One-language sites, crawlers and automation get nothing. The card is fixed
(no layout shift), appears 1.5 s after the page settles and the tab is visible, and never takes focus. Esc inside it,
or the close button, dismisses.

## What it remembers

One key, `cfg.ui.locale_hint` (`CFG_KEYS.uiLocaleHint`, via `cfgStorage`): the last site locale shown and the dismissed
pairs `"<offered>><shown>"` with a date. A dismissal silences that pair for `ttlDays` (180), not the hint in general.
Switching language yourself (switcher, URL, the button) closes the pair too.

## `exclude`

Pathname prefixes or RegExps matched against `location.pathname` **including the locale prefix** (`/en/legal`). Use it
for pages whose language is fixed by meaning.

## Copy

Self-contained, 17 locales in `i18n/locales/`, written in the **browser's** language (the card carries `lang` and `dir`)
with the target named in its own (`getLocaleMeta(code).native`). A browser language without a bundled dictionary reads
English. Add a string to `i18n/types.ts` and all 17 files; `dictionaries.test.ts` checks it.

Logic is in `decide.ts` (pure, tested), storage in `memory.ts`. Plan and rejected alternatives:
`frontend/@dev/active/locale-suggestion/PLAN.md`.
