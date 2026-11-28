/**
 * The product language for "a thing the player is playing".
 *
 * Framework-free on purpose: this type is read by a host's store, by the
 * player's surfaces, by a transcript block and by a file tree, and none of them
 * should have to agree on a React or transport shape to talk about a track.
 */

/** What kind of element has to play this. Nothing else varies by kind. */
export type MediaKind = "audio" | "video";

/**
 * One playable item.
 *
 * `src` is a resolved, playable URL — deriving it from a host + path is the
 * transport's job, never the store's. A credential in that URL is the
 * transport's business and must not leak into this vocabulary.
 *
 * `machineId` and `path` are carried for DISPLAY and for navigation ("open this
 * file in the tree"), not to re-derive `src`. Keeping both here is what lets the
 * player name where a track came from when its host goes away mid-play.
 */
export interface MediaTrack {
  /**
   * Stable identity for this track. Two loads with the same id are the same
   * track — the store uses it to answer "is this already playing?" without
   * comparing URLs, which can differ for one file (a download URL and a
   * playlist URL name the same `.mp4`).
   */
  readonly id: string;
  readonly kind: MediaKind;
  readonly src: string;
  /** Human-facing name, normally the file's basename. */
  readonly title: string;
  /** The host the file lives on, for the subtitle and for navigation. */
  readonly machineId?: string;
  /** Absolute path on that host, for the subtitle and for navigation. */
  readonly path?: string;
  /** Optional poster/cover art URL. */
  readonly poster?: string;
}

/**
 * What is known ABOUT a track, beyond what is needed to play it.
 *
 * Deliberately separate from {@link MediaTrack}: everything there is required to
 * make sound, everything here is required only to describe it, and the two
 * arrive at different times — a track plays the instant it is clicked, while its
 * description is a fetch that may never answer.
 *
 * Every field is optional because every field genuinely can be absent: a `.wav`
 * carries no artist, a stream carries no size, and a host that has gone away
 * has no name. A surface renders the rows it HAS rather than printing
 * "unknown" against the ones it does not — an empty label is noise, not
 * information.
 *
 * Framework-free and route-free, like the rest of this module: the strings are
 * already-formatted product values, so nothing here has to agree on a wire
 * shape or a locale.
 */
export interface MediaDetail {
  readonly artist?: string;
  readonly album?: string;
  /** Seconds. Distinct from the element's clock: this is the FILE's length. */
  readonly durationSeconds?: number;
  readonly sizeBytes?: number;
  readonly codec?: string;
  /** Pixels, for video. Both or neither. */
  readonly width?: number;
  readonly height?: number;
}

/**
 * Why playback stopped when it was not the user's doing.
 *
 * This is a closed vocabulary rather than a free string because the bar has to
 * NAME the cause. The failure this whole feature argues against is silence with
 * no explanation, and a generic `Error` object is how that gets reintroduced:
 * the machine going away mid-track is not "an error", it is a specific thing the
 * user can understand and act on.
 */
export type MediaFailure =
  /** The host holding the file became unreachable; the buffer ran out. */
  | { readonly reason: "machine-unreachable"; readonly machineId?: string }
  /** The server refused the media request (missing credentials, or a gone file). */
  | { readonly reason: "refused" }
  /**
   * The browser refused to start playback without a user gesture.
   *
   * Not a `MediaError` at all: it arrives as a `DOMException` rejecting the
   * `play()` promise, so it is a different source with a different type. It is
   * also the only member here that is not a fault — the file is fine and one
   * click fixes it — which is why it must not read as "something broke".
   */
  | { readonly reason: "blocked" }
  /** The element failed for a reason the browser did not attribute. */
  | { readonly reason: "unknown" };

/** Build a track id from the pair that actually identifies a file. */
export function mediaTrackId(machineId: string | undefined, path: string): string {
  return machineId ? `${machineId}:${path}` : path;
}

/** The basename of a path, for a default title. Tolerates both separators. */
export function mediaTitleFromPath(path: string): string {
  const parts = path.split(/[/\\]/);
  return parts[parts.length - 1] || path;
}

/** What a caller knows about a file on a host, before it is a track. */
export interface MachineTrackInput {
  readonly kind: MediaKind;
  /** The URL that plays. Derived by the transport; it may carry a credential. */
  readonly src: string;
  readonly machineId: string;
  readonly path: string;
  /** Overrides the basename when the caller has a better name (an ID3 title). */
  readonly title?: string;
  /**
   * Artwork URL, supplied rather than derived.
   *
   * This module names no routes — a domain type that knew the server's URL shape
   * would make the product language depend on a wire contract. The caller
   * derives it, which is where that knowledge lives.
   */
  readonly poster?: string;
}

/**
 * THE constructor for a track that lives on a host.
 *
 * One function because a track was previously assembled by hand at every entry
 * point — a click on a transcript chip, a row in a file tree, a deep link — and
 * each spelled out the same four fields. That is not a style problem: `poster`
 * was added to the type and to ONE of those call sites, so artwork appeared on
 * hover in the transcript and never in the player, for months, with nothing
 * failing. Optional fields make an incomplete construction indistinguishable
 * from a deliberate one.
 *
 * Every entry point goes through here, so a field added to `MediaTrack` is added
 * to all of them at once or to none.
 */
export function machineTrack(input: MachineTrackInput): MediaTrack {
  return {
    // The PAIR identifies the file, not the URL: one file has two URLs (a
    // download and a playlist), and keying on the URL would make the same file
    // read as two different tracks depending on which door it came through.
    id: mediaTrackId(input.machineId, input.path),
    kind: input.kind,
    src: input.src,
    title: input.title || mediaTitleFromPath(input.path),
    machineId: input.machineId,
    path: input.path,
    ...(input.poster ? { poster: input.poster } : {}),
  };
}
