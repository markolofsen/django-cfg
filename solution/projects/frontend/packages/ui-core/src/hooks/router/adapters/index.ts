// Adapters live behind sub-path imports so framework-specific peer
// deps (next, react-router, etc.) load only when the consumer asks
// for them. Do NOT re-export adapters from the package barrel — that
// would force every consumer to resolve all peer deps.
export type {} from '../adapter';
