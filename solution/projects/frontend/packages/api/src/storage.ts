/**
 * `@djangocfg/api/storage` — the browser-storage key registry on its own.
 *
 * Zero dependencies and no client: packages that only need a key, a guarded
 * read/write or `createStorage('<owner>')` import this, not the generated SDK.
 * The source is the handwritten runtime key registry.
 */
export { readCookie } from './cookies';
// Single sign-in host: pure helpers (no React, edge-safe) for middleware and the generated clients.
export {
  buildSsoLoginUrl,
  deriveAuthHost,
  hasReturnMarker,
  markReturn,
  stripReturnMarker,
  SSO_ERROR,
  SSO_RETURN,
  parseSsoHost,
  registrableDomain,
  resolveSso,
  safeNext,
} from './auth/utils/sso';
export type { SsoConfig, SsoOffReason, SsoState } from './auth/utils/sso';
export {
  CFG_FAMILIES,
  CFG_KEYS,
  cfgStorage,
  createStorage,
  normalizeSegment,
} from './runtime/keys';
export type {
  FamilySpec,
  GuardedStorage,
  KeySpec,
  KeyStore,
  StorageOptions,
  WriteOptions,
} from './runtime/keys';
