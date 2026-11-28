/**
 * @djangocfg/realtime — the framework-free core: protocol v1, the client, its
 * read-model store. No React and no DOM here; React lives in `./react`, the
 * debug panel in `./debug`, the in-memory server in `./testing`.
 */
export * from './client';
export * from './protocol';
export * from './store';
