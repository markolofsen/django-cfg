'use client';

/** Public surface for `@djangocfg/widget-data/json-tree`. */

export { JsonTree, JsonTree as default } from './JsonViewer';
export type { JsonTreeProps, JsonValue, JsonAction, JsonSize } from './types';

// In the retired ui-tools the `./json-tree` subpath resolved to `lazy.tsx` and this barrel
// was unreachable — the inverse of the other seven tools, whose subpath
// resolved here and left their `Lazy*` dead. One barrel now carries both.
export { LazyJsonTree } from './lazy';
