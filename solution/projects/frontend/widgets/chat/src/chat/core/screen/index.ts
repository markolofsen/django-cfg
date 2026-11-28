// What the reader's screen does: where the bottom is, what arrived while they were away, which row is the tab stop, how much of a phone is visible.
//
// In core/ because none of it is DOM: numbers, lists and decisions, testable without a renderer.
//
// *   Scroll. HOW to follow the bottom is not here and must not come back: it needs the engine's own scroll settle
//     to blend against, which a pure model cannot see, and a hand-written version shook on every fling.
//     `use-stick-to-bottom` owns the motion, wired in primitives/. WHETHER an arrival was the reader's own send
//     is a different question, and one the library cannot answer at all: `isOwnSend` decides it from the transcript
//     alone, which is why it is testable here and the animation is not.
// *   Focus. The DOM part of the transcript's single tab stop is three lines and lives in primitives/; the part that
//     can be wrong (which index a key selects, and what happens when the list shrinks under a stale one) lives here.
// *   Viewport. The phone's visible area and the browser-history stack of open layers.
//
// May import: utils.

export { MissedCount, missedRows } from "./missed";
export type { MissedRole } from "./missed";
export { isOwnSend } from "./sent";
export type { SentRole } from "./sent";
export { PIN_THRESHOLD, SETTLE_MS, distanceFromBottom, nextPinned } from "./pin";
export type { ScrollMetrics } from "./pin";
export { CHAT_ITEM_ATTR, clampIndex, isRovingKey, nextIndex } from "./roving";
export type { RovingKey } from "./roving";
export { KEYBOARD_MIN, boxVars, readViewportBox } from "./box";
export type { ViewportBox, ViewportSample } from "./box";
export { push as pushLayer, reconcile as reconcileLayers, release as releaseLayer, settle as settleLayers } from "./back-stack";
export type { Entry as LayerEntry } from "./back-stack";
