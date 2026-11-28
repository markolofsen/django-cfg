// ↑/↓ prompt recall: the boundary rules and the ladder they walk.
//
// Pure by design — the surface is meant to be swappable without retesting any
// of this. May import: nothing.

export {
  atFirstLine,
  atLastLine,
  bufferIsRecallOwned,
  type ComposerCaret,
} from "./boundary";
export {
  REST,
  recallNext,
  recallPrevious,
  type RecallLadder,
  type RecallMove,
  type RecallPosition,
  type RecallState,
} from "./ladder";
// Where the `sent` rungs come FROM. `ladder.ts` walks the ladder; this builds
// the one array it walks, out of the transcript rather than a local cache.
export { ladderFromMessages } from "./from-transcript";
