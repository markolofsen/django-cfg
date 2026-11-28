// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Re-export of the @chenglou/pretext public types. A hand-written mirror used
// to live here to keep `pnpm check` green while the runtime was an optional
// dependency; it is a hard `dependencies` entry now, and the mirror had already
// drifted — it declared `LayoutLine.start/end` as `number` where upstream
// returns a `{ segmentIndex, graphemeIndex }` cursor, so every consumer of
// `usePretextLines` was typed against a shape the runtime never produces.

export type {
  PrepareOptions,
  PreparedText,
  PreparedTextWithSegments,
  LayoutResult,
  LayoutLine,
  LayoutLineRange,
  LayoutLinesResult,
  LayoutCursor,
} from '@chenglou/pretext';

import type * as pretext from '@chenglou/pretext';

/** The subset of the module surface the hooks in this folder call. */
export type PretextModule = Pick<
  typeof pretext,
  'prepare' | 'prepareWithSegments' | 'layout' | 'layoutWithLines' | 'walkLineRanges'
>;
