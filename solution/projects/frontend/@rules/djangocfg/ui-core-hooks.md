---
title: "ui-core — hook catalogue"
status: current
version: "1.0"
audience: frontend, agents
last_reviewed: 2026-09-11
---

# `@djangocfg/ui-core` — hooks

Every hook, by topic. Import from `@djangocfg/ui-core` (or
`@djangocfg/ui-core/hooks`; do not mix both in one file).

## The ones worth knowing before you write your own

| Need | Hook |
|---|---|
| Is this a small viewport | `useIsMobile` (<768px), `useIsPhone`, `useIsTabletOrBelow`, or `useMediaQuery` |
| Is this a touch device | `useIsTouch` — **not** the same question as mobile |
| Read/write a query param as state | `useQueryState`, or `useQueryParams` for several |
| Navigate | `useNavigate` / `useRouter` / `useLocation` — router-adapter aware |
| Countdown to a deadline | `useCountdown` / `useCountdownFromSeconds` |
| Is this nav item current | `useIsActive` |
| Back, but not off-site | `useBackOrFallback` |
| Persist a value | `useLocalStorage` / `useSessionStorage` / `useStoredValue` |
| Debounce | `useDebounce` (value) or `useDebouncedCallback` (function) |
| Copy to clipboard | `useCopy` — **not** `useClipboard`, which does not exist |
| Element size | `useSize` / `useResizeObserver` |
| Lock body scroll behind an overlay | `useBodyScrollLock` |
| Toast | `useToast` |
| Is this browser tab active / the leader | `useIsTabActive` / `useIsTabLeader` |
| Keyboard shortcut | `useHotkey`, `useHotkeyChord`, `useHotkeyHelp` |
| Resolved light/dark | `useResolvedTheme` |

## Traps

- **`useResizeObserver` + a synchronous `scrollTop` write corrupts a virtualised
  list.** Never write `scrollTop` synchronously inside a ResizeObserver callback
  over `react-virtuoso`: it corrupts the size cache and the transcript renders
  blank with duplicate `data-index` rows.
- **There is no `useTheme`.** Read `useResolvedTheme`, or the theme provider from
  [`@djangocfg/layouts`](layouts.md).
- **Router hooks need the adapter.** Without the Next adapter mounted they fall
  back to the History API and the App Router never sees the navigation.

<!-- GENERATED:start -->
_57 hooks in 13 topics. Generated from `ui-core/src/hooks/` — do not hand-edit._

| Topic | Exports | Names |
|---|---|---|
| `audio` | 3 | `useAudioPrefs` · `useNotificationSounds` · `useSoundEffect` |
| `debug` | 1 | `useDebugTools` |
| `device` | 3 | `useBrowserDetect` · `useDeviceDetect` · `useShortcutModLabel` |
| `dom` | 11 | `useBodyScrollLock` · `useCopy` · `useFormReset` · `useImageLoader` · `useIsScrolling` · `useLayoutEffect` · `useResizeObserver` · `useScroll` · `useScrollDirection` · `useScrollPosition` · `useSize` |
| `events` | 1 | `useEventListener` |
| `feedback` | 1 | `useToast` |
| `hotkey` | 5 | `useHotkey` · `useHotkeyChord` · `useHotkeyHelp` · `useHotkeysContext` · `useRegisterHotkey` |
| `media` | 5 | `useIsMobile` · `useIsPhone` · `useIsTabletOrBelow` · `useIsTouch` · `useMediaQuery` |
| `router` | 12 | `useBackOrFallback` · `useHashState` · `useIsActive` · `useLocation` · `useLocationProperty` · `useNavigate` · `useQueryParams` · `useQueryState` · `useRouter` · `useRouterAdapter` · `useSmartLink` · `useUrlBuilder` |
| `state` | 8 | `useCallbackRef` · `useDebounce` · `useDebouncedCallback` · `useLocalStorage` · `usePrevious` · `useSessionStorage` · `useStateMachine` · `useStoredValue` |
| `tabs` | 4 | `useActiveTab` · `useActiveTabStore` · `useIsTabActive` · `useIsTabLeader` |
| `theme` | 1 | `useResolvedTheme` |
| `time` | 2 | `useCountdown` · `useCountdownFromSeconds` |
<!-- GENERATED:end -->

## Where to look next

`packages/ui-core/src/hooks/<topic>/<name>.ts` in the djangocfg checkout.
