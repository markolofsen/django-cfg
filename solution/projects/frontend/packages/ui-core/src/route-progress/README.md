# route-progress

The thin bar at the top of the window between pages, and the per-page switches for it and for the scroll jump. Our own code; the progress model comes from `nprogress` (see [NOTICE](NOTICE)). Plan and decisions: `frontend/@dev/planned/route-progress-module/PLAN.md`.

Subpath: `@djangocfg/ui-core/route-progress`. `BaseApp` mounts the provider; apps normally only call `useNavigationBehavior`.

| Folder | Job |
|---|---|
| `engine/` | the state machine: `start`, `set`, `inc`, `done`, `cancel`; no DOM, no React |
| `view/` | `<RouteProgressBar>`: `scaleX` bar, tokens, reduced motion |
| `triggers/` | which link clicks start the bar; page-hide and bfcache reset |
| `behavior/` | the lease store behind `useNavigationBehavior` |
| `provider/` | `RouteProgressProvider`, the context, and the one rule `shouldStartProgress` |

## Who decides, in order
1. the call's `progress` option (`push(url, { progress })`);
2. the app switch (`BaseApp progressBar={false}` wins over everything);
3. a mounted page's `useNavigationBehavior({ progress: false })`;
4. the app's `shouldShow(from, to)`, if set;
5. the default: the pathname changes (`?query` and `#hash` do not).

## Styling
CSS variables on any ancestor: `--route-progress-color` (default `--primary`), `--route-progress-height` (3px), `--route-progress-z` (1600). One anchor can opt out: `<a data-no-route-progress>`.

## Adding a trigger
A trigger is a function that calls `engine.start()` and returns its unsubscribe; add it to `triggers/attach.ts`. Ending a run is the router wiring's job (`NextRouterAdapter` calls `engine.done()` on commit); the engine's ceiling ends a run nobody finished.
