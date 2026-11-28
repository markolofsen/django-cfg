import { Slider } from "@djangocfg/ui-core";
import { cn } from "@djangocfg/ui-core/lib";
import { formatClock } from "@djangocfg/widget-kit";

import { usePlayerCopy } from "../i18n";
import { playedFraction } from "../model";

/**
 * Steps per track, whatever its length.
 *
 * The slider works in STEPS, not seconds, so an arrow key moves a sensible
 * distance in a 30-second clip and in a two-hour recording alike. Seconds as the
 * unit would make one arrow press 0.1% of a long file, which is a control that
 * appears not to respond.
 */
const STEPS = 1000;

/** Below this the bar is a read-out: a file whose length is unknown cannot be moved through. */
const SEEKABLE_MIN_DURATION = 0;

export interface SeekBarProps {
  /** Seconds elapsed, as the element reports them. */
  readonly position: number;
  /** Total seconds. Zero before metadata arrives. */
  readonly duration: number;
  /** Seconds buffered ahead of the start. Drawn behind the played range. */
  readonly buffered?: number;
  /** True while the user is dragging. The store owns this, not the slider. */
  readonly scrubbing?: boolean;
  /** Where the finger is, in seconds, while `scrubbing`. */
  readonly scrubPosition?: number;
  /** A failure mutes the bar — see `failed`. */
  readonly failed?: boolean;
  readonly onScrubStart: (position: number) => void;
  readonly onScrubMove: (position: number) => void;
  readonly onScrubEnd: () => void;
}

/**
 * The row's progress meter, made live.
 *
 * Not a new control: this is the affordance the row already drew, given the
 * behaviour a reader assumes it has. A 40-minute recording that can be started
 * and stopped but not moved through is a player in name only.
 *
 * ## The one hard part is the drag
 *
 * The element keeps playing while a finger is on the thumb, so its `timeupdate`
 * and the pointer are two writers of one number. The guard is that the store
 * stops mirroring the clock while `scrubbing`, and this component renders
 * `scrubPosition` instead of `position` in that state. Without it the thumb
 * snaps back to the playhead between pointer moves.
 *
 * Three of the four reference players guard it this way; the one that does not
 * gets away with it only because its clock is a 500ms poll.
 *
 * ## Why a shared primitive rather than an `<input type="range">`
 *
 * Keyboard, `aria-valuenow`, RTL, the drag capture and the touch handling all
 * come with Radix. A raw range input would re-implement each, and would need an
 * allowlist entry in `check-raw-controls` claiming no primitive fits — which is
 * not true.
 */
export function SeekBar({
  position,
  duration,
  buffered = 0,
  scrubbing = false,
  scrubPosition = 0,
  failed = false,
  onScrubStart,
  onScrubMove,
  onScrubEnd,
}: SeekBarProps) {
  const copy = usePlayerCopy();

  // The DRAG wins while it lasts. This is the render half of the guard whose
  // other half is the store refusing to mirror the clock — both are needed: one
  // stops the value being overwritten, this one shows the pointer's value even
  // on the render that arrives before the store hears about the move.
  const shown = scrubbing ? scrubPosition : position;
  const seekable = duration > SEEKABLE_MIN_DURATION;

  const step = seekable ? duration / STEPS : 1;
  const value = seekable ? Math.min(duration, Math.max(0, shown)) : 0;

  // Buffered goes INSIDE the slider's track, through the primitive's own
  // decoration slot. One quantity, one scale, one element that owns the
  // geometry — an overlay outside the slider would be a second author of where
  // the track begins and ends.
  const bufferedPercent = playedFraction(buffered, duration) * 100;
  const bufferedNode = (
    <span
      aria-hidden
      className="absolute inset-y-0 left-0 bg-muted-foreground/30"
      style={{ width: `${bufferedPercent}%` }}
    />
  );

  // data-before-jsx (`@rules`, gated by check-jsx-boundary).
  const clock = seekable ? `${formatClock(shown)} / ${formatClock(duration)}` : formatClock(shown);

  const onValueChange = (next: number[]) => {
    const seconds = next[0];
    if (seconds === undefined) return;
    // The FIRST change of a gesture is the grab. Radix fires `onValueChange` for
    // a click on the track too, which has no pointerdown-on-thumb to hook — so
    // the drag is opened here and closed by `onValueCommit`, and a click becomes
    // a one-move drag that commits immediately.
    if (!scrubbing) {
      onScrubStart(seconds);
      return;
    }
    onScrubMove(seconds);
  };

  return (
    <Slider
      value={[value]}
      min={0}
      max={seekable ? duration : 1}
      step={step}
      disabled={!seekable}
      onValueChange={onValueChange}
      onValueCommit={onScrubEnd}
      trackDecoration={bufferedNode}
      aria-label={copy.controls.seek}
      // The bar is a bar, not a form field: the number a screen reader should
      // hear is a time, not a count of seconds.
      aria-valuetext={clock}
      // The parts are styled through the primitive's OWN props, not through
      // `[&_[data-slot=…]]` variants. Those were tried and measured: the track
      // stayed 6px and the thumb stayed fully opaque, because arbitrary
      // variants of that shape are not generated in this build. A class that is
      // never emitted fails silently — the markup looks styled and is not.
      trackClassName={cn(
        // A HAIRLINE at rest. At the primitive's 6px this read as a progress
        // bar mid-download and out-weighted the title beside it. It thickens on
        // hover, which is the moment it becomes a target rather than a status.
        //
        // NO transition at all. `transition-all` was here and it animated the
        // filled range's WIDTH, so every position update started a tween the
        // next update interrupted — the playhead stuttered rather than moved.
        //
        // Narrowing it to `transition-[height]` does NOT work: measured, that
        // arbitrary variant is not generated in this build and the element
        // inherited `transition-property: all` — the class looks like a fix and
        // is not. No standard utility covers height, so the thickening simply
        // snaps, which at 3px→6px on hover is not something an eye tracks.
        "h-[3px]",
        "group-hover:h-1.5 group-focus-within:h-1.5",
      )}
      // A failure mutes the bar. A range still creeping forward under "the
      // machine went away" is the looks-healthy-while-silent shape this package
      // removes.
      rangeClassName={cn(failed && "bg-destructive")}
      thumbClassName={cn(
        // Smaller than the primitive's default: 16px on a 3px line is a handle
        // with no bar under it.
        "size-3 transition-opacity",
        // Hidden at rest, so an idle row keeps the thin unadorned line it had
        // before this was a control.
        !scrubbing && "opacity-0",
        "group-hover:opacity-100 group-focus-within:opacity-100",
      )}
      className={cn(
        // A taller hit area than the line it draws. Fitts's law, and the reason
        // every reference gives its scrubber a transparent margin: a hairline is
        // a target a pointer misses. The height is padding AROUND the track.
        //
        // A plain `group`, not `group/seek`: the NAMED variant generated zero
        // rules — measured, the stylesheet contained no `group-hover/seek` at
        // all — so the hover state silently never applied. The group is what
        // lets the track and thumb react to a hover on this whole 16px band
        // rather than on the 3px line itself.
        "group mt-1.5 h-4",
      )}
    />
  );
}
