import type { MediaTrack } from "../domain";

import { usePlayerCopy } from "../i18n";

export interface PlayerStageProps {
  /**
   * The loaded track, or null when nothing is playing.
   *
   * Null is a REAL state here and not an error: the stage has its own address,
   * so a delivered link opens on a cold load with nothing loaded. It must say so
   * rather than render an empty frame, which reads as broken.
   */
  readonly track: MediaTrack | null;
}

/**
 * The stage: the route where a track is watched full-size.
 *
 * This is the third option the console lacked. Video used to play only inside a
 * message bubble, which meant navigating away killed it — so the transcript had
 * to be a player, and that exception carried the whole audio/video asymmetry.
 * Once a video has somewhere else to be seen, the bubble goes back to being a
 * bubble.
 *
 * ## It does not hold the element, and it has no transport
 *
 * Both would be a second owner. The element stays mounted in the dock — the one
 * mount site — and the dock's frame grows to cover this area while the route is
 * open; what changes is geometry, never the parent, because changing the parent
 * recreates the node and restarts the track. The dock's row also stays on screen
 * underneath, carrying play, pause, the clock and the way back.
 *
 * So this screen owns exactly what the dock cannot: the ADDRESS, the artwork for
 * a track with no picture, and the honest empty state. Everything it appears to
 * be missing is one row below it.
 */
export function PlayerStage({ track }: PlayerStageProps) {
  const copy = usePlayerCopy();

  // Nothing loaded — a stale deep link, not an error. It says so, rather than
  // leaving a black rectangle that reads as a broken video.
  if (track === null) {
    return (
      <div
        role="region"
        aria-label={copy.stage.label}
        className="flex h-full items-center justify-center"
      >
        <span className="text-sm text-muted-foreground">{copy.stage.empty}</span>
      </div>
    );
  }

  // A loaded track needs NOTHING here: the dock's frame is already covering this
  // area with the real element. Drawing a placeholder underneath would show
  // through during the frame's transition and read as a second, broken player.
  //
  // There is no artwork branch. This route is reachable only for video
  // (`canOpenStage`), so a poster branch here was code nothing could route to —
  // and reviving it for audio would restore the two-owners problem that giving
  // audio its own full-screen answer created in the first place. Artwork now
  // has a home on the row and in the metadata popover, both of which are
  // reachable without leaving the page.
  return <div role="region" aria-label={copy.stage.label} className="h-full" />;
}
