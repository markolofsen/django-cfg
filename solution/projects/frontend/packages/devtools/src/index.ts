/**
 * @djangocfg/devtools — client entry.
 *
 * One package for frontend observability in django-cfg apps:
 * - `<Devtools />`: error/console capture + backend ingest + debug panel
 * - `devtools`: imperative capture API + component-scoped local loggers
 * - also available in the browser console as `window.devtools`
 *
 * Server-side reporting lives in `@djangocfg/devtools/server`.
 */

// The component
export { Devtools } from './Devtools'
export type { DevtoolsProps } from './Devtools'

// Imperative API
export { devtools } from './instance'
export type { DevtoolsApi } from './instance'

// Store (advanced: custom tabs subscribing to the entry feed)
export { devtoolsStore } from './store'
export type { DevtoolsState } from './store'

// Types
export { EventLevel, EventType } from './types'
export type {
  CustomDebugTab,
  DevtoolsConfig,
  DevtoolsEvent,
  DevtoolsStatus,
  LogEntry,
  Logger,
  LogLevel,
  ServerDevtoolsConfig,
} from './types'

// Panel pieces (for apps that want the panel without the auto button)
export { DevtoolsButton } from './panel/DevtoolsButton'
export type { DevtoolsButtonProps } from './panel/DevtoolsButton'
export { DevtoolsPanel } from './panel/DevtoolsPanel'
export type { DevtoolsPanelProps } from './panel/DevtoolsPanel'

// Utilities
export { useDebugMode } from './useDebugMode'
export { getSessionId, isDevelopment, isProduction } from './internal'
