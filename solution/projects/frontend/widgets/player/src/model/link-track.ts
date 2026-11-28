import { machineTrack, type MediaKind, type MediaTrack } from "../domain";

/**
 * Turning an address into a track, without knowing what a transport is.
 *
 * A deep link carries a host and a path and nothing else. Everything the
 * player needs beyond that — is this audio or video, what URL actually plays,
 * does a credential gate it — is the transport's to answer, and none of it can
 * be imported here: this package renders in Storybook with no transport and no
 * store.
 *
 * So the caller supplies the two answers and this composes the track. The seam
 * is what keeps the composition testable: the rules below (a kind that is not
 * playable resolves to nothing; the id is the machine+path pair, never the URL)
 * are the part that can be wrong, and they are pure.
 */

/** What a caller must resolve before a track can exist. */
export interface LinkResolution {
  /**
   * The playable kind, or undefined when this file is not media at all.
   *
   * Decided from the path by the transport's one extension table — never here,
   * and never from the URL, which for video is a playlist that names no file.
   */
  readonly kind: MediaKind | undefined;
  /**
   * The URL that plays. Derived by the transport, because it may carry a
   * credential — which is exactly why it is not in the address bar.
   */
  readonly src: string;
  /**
   * Artwork URL, supplied for the same reason `src` is: this module names no
   * routes. Offered for BOTH kinds — a video carries its own first frame, but a
   * file with embedded artwork is answered by the same route, and the element
   * shows a poster before it has decoded anything, which is the gap this fills
   * for a track opened cold from an address.
   */
  readonly poster?: string;
}

/**
 * The track a link names, or null when it names nothing playable.
 *
 * Null rather than a thrown error: a pasted link to a `.txt` is not a failure
 * to report, it is an address with no track behind it, and the stage already
 * renders that honestly as its empty state.
 */
export function trackFromLink(
  machineId: string,
  path: string,
  resolution: LinkResolution,
): MediaTrack | null {
  if (resolution.kind === undefined) return null;
  return machineTrack({
    kind: resolution.kind,
    src: resolution.src,
    machineId,
    path,
    poster: resolution.poster,
  });
}
