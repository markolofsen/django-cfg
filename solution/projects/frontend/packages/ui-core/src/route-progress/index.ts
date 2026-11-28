// Route progress: the thin top bar between pages and the per-page navigation switches.
// Engine (state machine) -> view (bar) -> triggers (link clicks) -> provider (one per app).

export { RouteProgressProvider } from './provider/RouteProgressProvider';
export type { RouteProgressProviderProps } from './provider/RouteProgressProvider';
export { useRouteProgress } from './provider/context';
export type { RouteProgressContextValue } from './provider/context';
export { shouldStartProgress } from './provider/shouldStart';

export { useNavigationBehavior } from './behavior/useNavigationBehavior';
export type { NavigationBehavior } from './behavior/store';

export { RouteProgressBar } from './view/RouteProgressBar';
export { createProgressEngine } from './engine/createProgressEngine';
export type { ProgressEngine, ProgressEngineOptions, ProgressState } from './engine/types';
export { NO_PROGRESS_ATTR } from './triggers/linkClick';
