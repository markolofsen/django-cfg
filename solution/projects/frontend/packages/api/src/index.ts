/**
 * @djangocfg/api — package entry point.
 *
 * Generated operations, React Query v5 hooks, Zod models, MSW mocks, and the
 * handwritten transport/session runtime.
 */

// Installs `window.__cfgAuth` (the auth trace reader) as soon as the package loads.
import './auth/trace';

export * from './_api';
export * from './runtime';
// What every generated operation can reject with; the generated shim names it as `ErrorType` (plan H2.5).
export type { ApiClientError } from './runtime/errors';
// Page params for the generated infinite queries (plan H2.7).
export { drfCursorParams, drfPageParams } from './runtime/pagination';

// Global runtime log-level control (role-aware verbosity).
export {
  getLogLevel,
  setLogLevel,
  onLogLevelChange,
  applyRoleLogPolicy,
  type ConsolaLevel,
} from './log-control';

// Env flags — single source of truth (api is the lowest shared package).
export { isDev, isProd, isBrowser, isStaticBuild } from './auth/utils/env';
