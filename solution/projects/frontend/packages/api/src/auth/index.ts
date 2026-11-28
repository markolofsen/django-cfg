/**
 * @djangocfg/api/auth
 *
 * Authentication module with contexts, hooks and utilities.
 * Use this entry point in client components.
 *
 * @example
 * ```tsx
 * 'use client';
 * import { AuthProvider, useAuth } from '@djangocfg/api/auth';
 *
 * export function MyApp({ children }) {
 *   return (
 *     <AuthProvider>
 *       {children}
 *     </AuthProvider>
 *   );
 * }
 *
 * export function Profile() {
 *   const { user, logout } = useAuth();
 *   return <div>{user?.email}</div>;
 * }
 * ```
 */

// Constants
export * from './constants';

// Persisted auth trace: `authTrace(ev, fields)` and the readers behind `window.__cfgAuth`.
export * from './trace';
import { registerAuthCopy } from './trace';
registerAuthCopy();

// Contexts
export * from './context';

// Hooks
export * from './hooks';

// Types (single source of truth)
export * from './types';

// Utils (validation, errors, analytics)
export * from './utils';
