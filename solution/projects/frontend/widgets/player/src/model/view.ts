import type { MediaFailure, MediaTrack } from "../domain";

/**
 * Everything the surfaces need to know, in the shape they render.
 *
 * A pure projection (`@rules/general/state-and-data.md`): the store keeps FACTS — a
 * track, a status, a clock — and this turns them into the questions a surface
 * actually asks. Deriving inside each surface would put the same three ternaries
 * in the dock and the stage, where they can disagree.
 */

/** Where the element is shown. Mirrors the store's own union. */
export type PlayerSurface = "dock" | "stage" | "detached";

/**
 * The status a surface renders, flattened from the store's union.
 *
 * The store's `failed` carries its cause; here the cause is lifted out to
 * `failure` so a surface asks one question ("is there a failure?") rather than
 * narrowing a union it did not define.
 */
export interface PlayerView {
  readonly track: MediaTrack;
  /** True when the user has asked for sound — intent, not the element's state. */
  readonly playing: boolean;
  /** The file reached its end on its own. */
  readonly ended: boolean;
  /** Present only when playback stopped for a reason worth naming. */
  readonly failure?: MediaFailure;
  readonly position: number;
  readonly duration: number;
  /**
   * Whether this track has a picture to show.
   *
   * NOT the same question as `kind === "video"` at every call site: it is the
   * one that decides whether the stage is worth opening, and keeping it here
   * means a future kind (a waveform-only video, an image) changes one line.
   */
  readonly hasPicture: boolean;
}

/**
 * The fraction played, for a progress bar. Zero until duration is known.
 *
 * Guarded because `duration` is `0` before metadata arrives and `NaN` for a
 * stream of unknown length — both of which render a bar at an undefined width
 * rather than at zero.
 */
export function playedFraction(position: number, duration: number): number {
  if (!Number.isFinite(duration) || duration <= 0) return 0;
  return Math.min(1, Math.max(0, position / duration));
}

/**
 * Whether the stage is worth offering for this track.
 *
 * Audio has nothing to look at, so a full screen of it is a worse view of the
 * same information the dock already shows. The control is absent rather than
 * disabled: a door that does not go anywhere is worse than no door.
 */
export function canOpenStage(track: MediaTrack): boolean {
  return track.kind === "video";
}
