import { forwardRef, type AudioHTMLAttributes, type VideoHTMLAttributes } from "react";
import HlsVideo from "hls-video-element/react";

/**
 * The ONE media element. Audio and video are the same component.
 *
 * `<audio>` and `<video>` share their entire scripted interface — play, pause,
 * currentTime, duration, volume, buffered, error — and differ only in whether
 * there is a picture. So the tag is a variable, and surfaces differ in the BOX
 * they draw around this component, not in which player they instantiate.
 *
 * That is what lets a video survive navigation without a second element ever
 * existing: one identity, one mount site, for the life of a track. Moving the
 * node between surfaces was tried and recreates it — see
 * `portal-move.stories.tsx`.
 *
 * ## The props are a discriminated union on purpose
 *
 * `poster` and `playsInline` are meaningless on an audio element. A single
 * `kind: MediaKind` field with one prop bag would let them through as attributes
 * the browser silently ignores. This shape makes them a type error instead.
 */
export type MediaElementProps =
  | (AudioHTMLAttributes<HTMLAudioElement> & { readonly kind: "audio" })
  | (VideoHTMLAttributes<HTMLVideoElement> & {
    readonly kind: "video";
    /**
     * The source is an HLS playlist rather than a plain file.
     *
     * A FACT about the source, supplied by whoever derived it — never sniffed
     * from the URL here. The transport owns the download-versus-playlist
     * decision, and re-deriving it from the string would make this a second
     * owner that silently disagrees the day a route changes.
     */
    readonly hls?: boolean;
  });

/**
 * A media element with no controls and no state of its own.
 *
 * `controls={false}` is not a style choice: the native control strip is a SECOND
 * owner of playback, able to start and seek without the store ever hearing about
 * it. Every control belongs to a surface, which drives this through the store.
 *
 * The ref is the only way to reach the element. Whoever mounts it hands the node
 * to the state layer, which subscribes to it — the state layer never creates an
 * element, because a store that built one would own a node it cannot see remount.
 */
export const MediaElement = forwardRef<HTMLMediaElement, MediaElementProps>(
  function MediaElement(props, ref) {
    // An HLS playlist needs a decoder `<video>` does not have outside Safari.
    // Without this the element stalls at `readyState` 0 and reports NOTHING —
    // no error event, no rejected play() — which is the silent failure this
    // package exists to remove. `<hls-video>` lazy-loads hls.js only where
    // native HLS is absent, so Safari still plays the playlist directly.
    //
    // It presents the same scripted interface as `<video>`, so everything above
    // — the ref, the store, every handler — is unchanged.
    if (props.kind === "video" && props.hls === true) {
      const { kind: _kind, hls: _hls, ...rest } = props;
      // The wrapper types its attributes narrower than React does (`preload` is
      // a literal union there, a plain string here), so the props are cast at
      // this boundary exactly as the plain-tag branch below casts its own. The
      // discriminated union already checked the caller.
      const Element = HlsVideo as unknown as "video";
      return <Element controls={false} {...(rest as VideoHTMLAttributes<HTMLVideoElement>)} ref={ref as never} />;
    }

    const { kind, ...rest } = props;
    const Tag = kind === "audio" ? "audio" : "video";
    // Cast at the ONE point the union collapses: `Tag` is a string variable, so
    // TS can no longer pair the tag with its own attribute set. The union above
    // already checked the caller; this is the boundary where that check ends.
    const Element = Tag as "audio";
    return <Element controls={false} {...(rest as AudioHTMLAttributes<HTMLAudioElement>)} ref={ref} />;
  },
);
