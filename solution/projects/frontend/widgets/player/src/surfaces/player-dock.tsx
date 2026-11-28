import { Maximize2, Minimize2, Pause, Play, X } from "lucide-react";
import type { ReactNode } from "react";
import { Button, Popover, PopoverContent, PopoverTrigger } from "@djangocfg/ui-core";
import { cn } from "@djangocfg/ui-core/lib";
import { formatClock } from "@djangocfg/widget-kit";
import type { MediaDetail, MediaFailure, MediaTrack } from "../domain";

import { usePlayerCopy } from "../i18n";
import { canOpenStage, failureText } from "../model";
import { PlayerInfo } from "./player-info";
import { SeekBar } from "./seek-bar";
import { TrackCover } from "./track-cover";
import { VolumeControl } from "./volume-control";

/**
 * The picture's edge in the row — artwork for audio, the video tile for video.
 *
 * ONE number for both kinds, so the row keeps a single shape whatever plays.
 * Sized to the row's own content height: anything taller pushes the row open.
 */
const ROW_COVER_SIZE = 36;

/**
 * The row's height, and the only geometry this component owns.
 *
 * It is a literal so Tailwind can SEE it. The scanner is textual and cannot
 * follow a constant, so a class name assembled from a variable is never
 * generated — the utility is silently absent and the element falls back to a
 * browser default. Measured: `bottom-8` written this way computed to `-56px`,
 * which put the whole dock below the viewport while every test stayed green.
 * Writing the value inline keeps the string in the class attribute, where the
 * scanner reads it.
 *
 * Everything else — where the row sits, how wide it is, what it clears — comes
 * from the shell's layout, because the row is a normal child of the content
 * column rather than a fixed overlay.
 *
 * 3.5rem holds TWO lines: the title (with the machine beside it) and the
 * scrubber. It briefly needed 4rem when the machine had a line of its own —
 * measured then at 52px of content in a 52.8px box, so the bar sat flush on the
 * bottom border. Putting the machine on the title line gave that height back.
 */
export const DOCK_HEIGHT = "h-[3.5rem]";

export interface PlayerDockProps {
  readonly track: MediaTrack;
  readonly playing: boolean;
  /** Present only when playback stopped for a reason worth naming. */
  readonly failure?: MediaFailure;
  /** True when the track played to its end. */
  readonly ended?: boolean;
  readonly position: number;
  readonly duration: number;
  /** Seconds buffered ahead of the start. Drawn behind the played range. */
  readonly buffered?: number;
  /** True while the user is dragging the scrubber. Owned by the store. */
  readonly scrubbing?: boolean;
  /** Where the finger is, in seconds, while `scrubbing`. */
  readonly scrubPosition?: number;
  readonly onPlay: () => void;
  readonly onPause: () => void;
  readonly onDismiss: () => void;
  readonly onScrubStart: (position: number) => void;
  readonly onScrubMove: (position: number) => void;
  readonly onScrubEnd: () => void;
  /** 0…1. The user's intent, not what the element reports. */
  readonly volume: number;
  readonly muted: boolean;
  readonly onVolumeChange: (volume: number) => void;
  readonly onToggleMuted: () => void;
  /**
   * False where the platform will not let script set `volume`. Measured by the
   * host, never sniffed from a user agent inside this package.
   */
  readonly canChangeVolume?: boolean;
  /**
   * Open the stage. Absent for a track with nothing to look at, so the control
   * does not appear rather than appearing dead.
   *
   * An INTENT, not a URL: the shell owns route literals
   * (`@rules/general/architecture-and-ownership.md`), and this component must never
   * learn that a player route exists.
   */
  readonly onOpenStage?: () => void;
  /**
   * Leave the stage. Required whenever `staged` is true: the frame covers the
   * screen above this row, so without it the reader has no way back that is not
   * the browser's own Back button.
   */
  readonly onLeaveStage?: () => void;
  /**
   * Reveal the file in its machine's tree.
   *
   * Reached from the CARD's footer, not from the title: navigating away is an
   * act the reader should choose, and the title's job is to show what is
   * playing. Absent ⇒ the footer offers copy alone rather than a dead button.
   */
  readonly onOpenInFiles?: () => void;
  /**
   * The media element, mounted by the host and placed here by this surface.
   *
   * A NODE, not something this component builds. The element is mounted once for
   * the life of a track and never moves — building one here would create a
   * second element the moment a second surface rendered, and two elements on one
   * source both make sound.
   *
   * For audio it is invisible and only has to stay in the tree; for video it
   * fills the thumbnail, which is the whole reason the dock takes it at all.
   */
  readonly element: ReactNode;
  /**
   * True while the stage route is open.
   *
   * The dock KEEPS the element even then — this is the one mount site, and
   * handing the node to another parent would recreate it and restart the track.
   * What changes is the frame's geometry: it leaves the row and fills the screen
   * above the footer, so the picture is where the reader is looking while its
   * position in the tree never moves.
   *
   * The row itself stays put and keeps working, which is what makes leaving the
   * stage free: the geometry changes back and nothing remounts.
   */
  readonly staged?: boolean;
  /**
   * Whether the metadata popover is open.
   *
   * A prop, not internal state: the store decides it, because a new track opens
   * it once and only the store knows a track is new. Local state here would be
   * a second answer to one question.
   */
  readonly expanded?: boolean;
  /**
   * Open or close the popover. Absent makes the title plain text, since nothing
   * on the row would then have a card to open.
   */
  readonly onExpandedChange?: (expanded: boolean) => void;
  /**
   * What is known about the file, for the popover. Absent while the description
   * is in flight, or for a track nothing describes.
   */
  readonly detail?: MediaDetail;
  /**
   * The machine's display NAME. Never its id — an opaque hash on screen is
   * correct and useless, and the roster holds a name for exactly this.
   */
  readonly machineName?: string;
  /** Open the machine. An intent; this component never learns a route exists. */
  readonly onOpenMachine?: () => void;
  /**
   * An address that reopens this track for someone else, for the card's footer.
   *
   * A VALUE built by the shell — the one exception to "intents, never URLs" in
   * this package, because a link that is COPIED rather than followed has to be
   * a string by the time it reaches a clipboard.
   */
  readonly shareUrl?: string;
}

/**
 * The footer dock: what is playing, where it came from, and the transport.
 *
 * ONE row with ONE transport. The design it replaces split the controls across a
 * status cell and a popover it opened, so a track had two play buttons and two
 * clocks — and for video the popover's transport drove an element mounted in a
 * message bubble somewhere else entirely.
 *
 * Apple-side: one row, one primary control, one dismissal, no settings. No
 * queue, no shuffle, no repeat, because the store holds exactly one track on
 * purpose, and no playback-rate control.
 *
 * **Volume lives behind an icon, not on the row.** The argument that the OS
 * already owns volume holds for a phone and fails in a browser: OS volume is not
 * per-tab, so turning a recording down means turning down the call it is playing
 * over. It is still the least-used of the three controls, so it costs a press
 * rather than the title's width.
 *
 * The dock is a REMOTE CONTROL with a picture attached. Watching happens on the
 * stage; this is what tells you something is playing, lets you move through it,
 * and lets you stop it.
 */
export function PlayerDock({
  track,
  playing,
  failure,
  ended = false,
  position,
  duration,
  buffered = 0,
  scrubbing = false,
  scrubPosition = 0,
  onPlay,
  onPause,
  onDismiss,
  onScrubStart,
  onScrubMove,
  onScrubEnd,
  volume,
  muted,
  onVolumeChange,
  onToggleMuted,
  canChangeVolume = true,
  onOpenStage,
  onLeaveStage,
  onOpenInFiles,
  element,
  staged = false,
  expanded = false,
  onExpandedChange,
  detail,
  machineName,
  onOpenMachine,
  shareUrl,
}: PlayerDockProps) {
  const copy = usePlayerCopy();

  const toggleLabel = playing ? copy.transport.pause : copy.transport.play;
  // The artwork drives the same act under a DIFFERENT name: the row renders two
  // controls for one intent, and two buttons a screen reader reads identically
  // are two buttons it cannot tell apart.
  const coverToggleLabel = playing
    ? copy.transport.pauseFromCover
    : copy.transport.playFromCover;
  const onToggle = playing ? onPause : onPlay;
  const stageOpener = canOpenStage(track) ? onOpenStage : undefined;

  // A failure REPLACES the clock rather than joining it: a running time next to
  // "the machine went offline" reads as though it were still playing. Naming the
  // cause is the entire point of this row.
  const failed = failure !== undefined;
  const message = failure ? failureText(failure, copy.failure) : null;

  // The clock follows the DRAG, not the playhead: while a finger is on the bar
  // the question it answers is "where would this land", and a read-out still
  // counting the audible position contradicts the thumb it sits beside.
  const clockPosition = scrubbing ? scrubPosition : position;
  const timeText = duration > 0
    ? `${formatClock(clockPosition)} / ${formatClock(duration)}`
    : formatClock(clockPosition);

  // The subtitle names WHERE the file is, which is what makes remote playback
  // legible: "this is playing from that machine, not from here".
  //
  // The machine's NAME, never its id. A raw id is what this row printed before —
  // `b2aacd578a11b4fb477e7721bd46f912` under the title — which is correct and
  // useless. With no name known the subtitle simply omits the machine rather
  // than falling back to the hash.
  //
  // The PATH is not here for EITHER kind. The row truncates to one line, so a
  // long path costs the machine its width and still ends in an ellipsis; the
  // popover states it in full and is available to audio and video alike. Video
  // used to keep the path only because it had no panel, and that exception goes
  // with the popover that replaced it.
  const location = machineName ?? "";

  // data-before-jsx (`@rules`, gated by check-jsx-boundary): every node decided
  // here, composed below.
  const toggleIcon = playing
    ? <Pause aria-hidden className="size-4" />
    : <Play aria-hidden className="size-4" />;

  // The NAME opens the card, it does not navigate.
  //
  // It used to jump straight to the file tree on the track's machine, which
  // leaves the page the reader was on to answer a question they had not asked.
  // The card states the same path and offers the folder as an explicit button,
  // so the destructive-feeling act is the one that costs a deliberate press.
  //
  // This is also how VIDEO reaches its metadata: its artwork is a door to the
  // stage and one click cannot mean two things, so the name carries the card
  // for both kinds and the ⓘ button is no longer needed by either.
  const titleButton = (
    <Button
      variant="link"
      size="sm"
      elevated={false}
      tooltip={copy.info.label}
      className="h-auto min-w-0 justify-start truncate p-0 text-sm font-medium"
    >
      {track.title}
    </Button>
  );

  const titleNode = onExpandedChange
    ? <PopoverTrigger asChild>{titleButton}</PopoverTrigger>
    : <span className="min-w-0 truncate text-sm font-medium" title={track.title}>{track.title}</span>;

  // The machine rides ON the title line, not under it.
  //
  // Two stacked lines plus the scrubber made three, which is what forced the
  // row from 3.5rem to 4rem and left the bar with 5px of clearance. One line
  // gives that height back and reads as one fact — "this track, from there" —
  // rather than as a heading with a caption.
  //
  // A FAILURE still takes its own line: it is the one thing here that must not
  // be truncated away by a long title, and naming the cause is the row's
  // entire purpose when playback stops.
  const locationNode = location
    ? (
      <span className="shrink truncate text-xs text-muted-foreground" title={location}>
        {location}
      </span>
    )
    : null;

  const failureNode = message
    ? <span className="truncate text-xs text-destructive">{message}</span>
    : null;

  // Three mutually exclusive things occupy the status slot, and the order
  // matters: the clock, or "finished", or nothing when a cause took the subtitle
  // line. A track that reached its end must not keep showing `3:40 / 3:40`,
  // which reads as still playing.
  const statusNode = failed
    ? null
    : ended
      ? <span className="shrink-0 text-xs text-muted-foreground">{copy.transport.ended}</span>
      : (
        // The CLOCK is the one thing here the meter already says approximately,
        // so it is what yields on a phone: `hidden sm:inline` gives its width
        // back to the name. "Finished" and a failure both stay at every width —
        // neither is inferable from a bar.
        <span className="hidden shrink-0 font-mono text-xs tabular-nums text-muted-foreground sm:inline">
          {timeText}
        </span>
      );

  // One control, two directions. On the stage it is the way OUT — and it has to
  // exist, because the frame covers the screen above this row, so the row is the
  // only chrome left. A toggle whose label states what the next press does.
  const stageToggle = staged
    ? (onLeaveStage
      ? { onClick: onLeaveStage, label: copy.stage.minimize, icon: <Minimize2 aria-hidden className="size-4" /> }
      : null)
    : (stageOpener
      ? { onClick: stageOpener, label: copy.dock.expand, icon: <Maximize2 aria-hidden className="size-4" /> }
      : null);

  // The transport leads the right-hand cluster: `outline` against the ghost
  // controls beside it, so the primary act stays the one thing the eye lands on
  // in a group of four.
  const transportButton = (
    <Button
      variant="outline"
      size="icon"
      elevated={false}
      onClick={onToggle}
      aria-label={toggleLabel}
      tooltip={toggleLabel}
      className="size-8 shrink-0 rounded-full"
    >
      {toggleIcon}
    </Button>
  );

  const stageButton = stageToggle
    ? (
      <Button
        variant="ghost"
        size="icon"
        elevated={false}
        onClick={stageToggle.onClick}
        aria-label={stageToggle.label}
        tooltip={stageToggle.label}
        className="size-8 shrink-0 rounded-full text-muted-foreground"
      >
        {stageToggle.icon}
      </Button>
    )
    : null;

  // The NAME opens the card for both kinds, so there is no ⓘ button on the row
  // at all — one control fewer in a right-hand cluster that had four.
  //
  // The PICTURE plays, for both kinds. Tapping the artwork to start a track is
  // what every music player does, and it puts the most-used act on the largest
  // target in the row rather than on a 32px glyph at the far end.
  //
  // Video used to open the STAGE from its thumbnail, which made one square in
  // one row mean two different things depending on the file. The stage keeps
  // its own control in the right-hand cluster, where it is a deliberate press
  // rather than the thing a pointer lands on first.

  // The element's box, and the ONE thing a surface change is allowed to touch.
  //
  // Three geometries, one mount site. The element never changes parent, so none
  // of these can interrupt playback — that is the whole design, and the reason
  // the stage is a geometry here rather than a component that takes the node.
  //
  //   staged video  the frame leaves the row and fills the screen above the
  //                 footer. `fixed` takes it out of flow so the row keeps its
  //                 own height and the transport stays reachable underneath.
  //   docked video  a real thumbnail, which is the picture that makes a dock
  //                 worth having.
  //   audio         a 1x1 transparent box, NOT `display: none`. A hidden subtree
  //                 stops laying out, and `display:none` on a media element is
  //                 where a browser may release the decoder.
  const stagedVideo = staged && track.kind === "video";
  const frameClass = stagedVideo
    // Anchored to the ROW: `bottom-full` puts the frame's bottom edge exactly on
    // the row's top edge, so the picture never covers the transport no matter
    // what sits below the row.
    //
    // Measuring from the COLUMN was tried and is wrong — `.main` includes the
    // status bar, so an inset equal to the row's height stopped 32px too low and
    // the picture overlapped the transport by exactly that much.
    //
    // The height is `100vh` and the frame is CLIPPED by the column's `overflow`,
    // rather than being sized to the column: any expression for "the column
    // minus this row" would have to name the row's height a second time, and
    // that number is the one thing here that can silently drift.
    ? "absolute inset-x-0 bottom-full z-30 flex h-screen items-center justify-center bg-black"
    : track.kind === "video"
      // A SQUARE tile of the same edge as audio's artwork, so the row keeps one
      // shape whatever is playing rather than two boxes of different widths.
      //
      // The 16:9 tile this replaces was geometrically correct — measured at
      // 71x40 — and still read as a black rectangle, because `object-contain`
      // fills whatever the source does not cover with the tile's background, so
      // any clip that is not exactly 16:9 shows bars. Pairing a square with
      // `object-cover` crops instead, so no letterbox exists at any ratio.
      //
      // It is never `hidden` — a display:none subtree stops laying out, and on
      // a media element that is where a browser may release the decoder.
      ? "relative shrink-0 overflow-hidden rounded-md bg-muted"
      : "pointer-events-none absolute size-px opacity-0";

  // The artwork, as the PLAY control.
  //
  // The label states what the next press DOES, so it tracks the transport
  // button rather than naming the picture — two controls for one act must not
  // announce themselves differently.
  // No `title` here either, for the same reason the staged picture has none:
  // this is artwork, and a caption over it says what pressing it already does.
  // The accessible name stays, so the control is not nameless.
  const coverButton = (
    <button
      type="button"
      onClick={onToggle}
      aria-label={coverToggleLabel}
      className="shrink-0 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <TrackCover src={track.poster} kind={track.kind} size={ROW_COVER_SIZE} path={track.path} />
    </button>
  );

  const infoContent = (
    // `side="top"` because the dock is a footer: opening downward would render
    // the panel off the bottom of the viewport.
    <PopoverContent side="top" align="start" className="w-80">
      <PlayerInfo
        track={track}
        detail={detail}
        machineName={machineName}
        onOpenMachine={onOpenMachine}
        onOpenInFiles={onOpenInFiles}
        shareUrl={shareUrl}
      />
    </PopoverContent>
  );

  // The docked video tile takes its edge from the SAME constant as audio's
  // artwork, as a style rather than a class: Tailwind's scanner is textual and
  // never generates a size assembled from a variable, so a second literal here
  // is how the two tiles would silently drift apart.
  //
  // Staged, the frame is sized by its own class and must not carry a 36px box.
  const frameStyle = !stagedVideo && track.kind === "video"
    ? { width: ROW_COVER_SIZE, height: ROW_COVER_SIZE }
    : undefined;

  const frame = (
    <div className={frameClass} style={frameStyle} data-testid="player-dock-frame">
      {element}
    </div>
  );

  // The wrapper is ALWAYS a button and always the frame's parent. Rendering the
  // frame bare in one state and wrapped in another changes the element's
  // parent, and React reconciles that as a remount: the node is recreated, the
  // source reloads and the track restarts at zero. That is not theory here — a
  // conditional wrapper is what `CrossingSurfacesKeepsTheSameElement` caught.
  //
  // The picture PLAYS, docked and staged alike. Clicking the frame to pause is
  // what a video player does everywhere, and it is the same act the row's
  // artwork performs for audio — so one square in one row cannot mean two
  // different things depending on the file. The stage keeps its own control in
  // the right-hand cluster.
  const pictureNode = track.kind === "video"
    ? (
      // NO `title`. The accessible name stays — without it the control is
      // nameless to a screen reader — but the browser's native tooltip does not
      // belong on a picture. Staged, this button is the whole screen, so the
      // tooltip surfaced wherever the pointer happened to rest over the video
      // and flipped between "play" and "pause" as the state changed. A tooltip
      // is for a control whose purpose is not obvious; clicking a video to
      // pause it needs no caption.
      <button
        type="button"
        onClick={onToggle}
        aria-label={coverToggleLabel}
        className={cn(
          "rounded outline-none focus-visible:ring-2 focus-visible:ring-ring",
          // Staged, the button is only a passive holder: it must not impose the
          // row's `shrink-0` on a frame that has left the row entirely.
          stagedVideo ? "contents" : "shrink-0",
        )}
      >
        {frame}
      </button>
    )
    : (
      // Audio's picture slot. `TrackCover` rather than a glyph: a track with
      // embedded artwork HAS something to show, and the row is where the reader
      // is looking. A file with no art falls back to the same tile the
      // transcript's rows use, so the row keeps one shape either way.
      //
      // The wrapper is ALWAYS a button and always the frame's sibling, even when
      // it does nothing — a conditional wrapper is a parent change, which React
      // reconciles as a remount, which restarts the track. Same rule the video
      // branch above follows, and the same story caught it.
      <>
        {coverButton}
        {frame}
      </>
    );

  // ONE popover provider around the whole row, because its trigger differs by
  // kind: the artwork for audio, the ⓘ button for video. Both anchor the same
  // content, so the metadata has a single owner however it is reached.
  //
  // The provider does NOT unmount anything — only `PopoverContent` is portalled
  // and torn down — so the media element inside the row's frame is untouched by
  // opening or closing. That is the distinction O6's objection turned on, and
  // `TogglingTheInfoPopoverKeepsTheSameElement` is what holds it.
  const row = (
    <div role="region" aria-label={copy.dock.label} className="shrink-0">
      <div
      className={cn(
        // A NORMAL ROW in the shell's content column — not a fixed overlay.
        //
        // Overlay was tried and it made the shell's layout something this
        // component had to re-derive: the row started at x=0 and its play
        // control landed on top of a rail icon, so the rail's width would have
        // had to be passed in or measured. That is a second owner of a number
        // the shell already knows. Placed in the column instead, position and
        // width come from the layout and there is no coordinate here at all.
        //
        // `relative` so the staged frame can anchor to THIS row's top edge with
        // `bottom-full` — see `frameClass`. That anchor is what keeps the
        // picture off the transport without naming the row's height twice.
        "relative z-40 flex shrink-0 items-center gap-3 border-t border-border/60 bg-card px-3",
        DOCK_HEIGHT,
      )}
    >
      {pictureNode}

      {/* `basis-0 flex-1` with a floor: the title and the location are the only
          parts of this row that say anything, so they get the leftover width and
          a minimum below which the row would be lying rather than truncating.
          Measured at 390px with a long name: without the floor the title
          collapsed to "20…" while the thumbnail kept its full 64px. */}
      <div className="flex min-w-[8rem] flex-1 basis-0 flex-col justify-center">
        {/* `min-w-0` on the title so IT yields first: the machine name is short
            and bounded, a filename is not, so letting the name shrink instead
            would truncate the wrong one. */}
        <div className="flex min-w-0 items-baseline gap-2">
          {titleNode}
          {locationNode}
        </div>
        {failureNode}
        <SeekBar
          position={position}
          duration={duration}
          buffered={buffered}
          scrubbing={scrubbing}
          scrubPosition={scrubPosition}
          failed={failed}
          onScrubStart={onScrubStart}
          onScrubMove={onScrubMove}
          onScrubEnd={onScrubEnd}
        />
      </div>

      {/* The clock rides WITH the transport rather than floating between the
          title and the controls. Measured before this: 12px from the title and
          82px from the play button, so it read as belonging to neither. */}
      <div className="flex shrink-0 items-center gap-2">
        {statusNode}
        {transportButton}
      </div>
      <VolumeControl
        volume={volume}
        muted={muted}
        onVolumeChange={onVolumeChange}
        onToggleMuted={onToggleMuted}
        canChangeVolume={canChangeVolume}
      />
      {stageButton}

      <Button
        variant="ghost"
        size="icon"
        elevated={false}
        onClick={onDismiss}
        aria-label={copy.transport.dismiss}
        tooltip={copy.transport.dismiss}
        className="size-8 shrink-0 rounded-full text-muted-foreground"
      >
        <X aria-hidden className="size-4" />
      </Button>
      </div>
    </div>
  );

  if (!onExpandedChange) return row;

  return (
    <Popover open={expanded} onOpenChange={onExpandedChange}>
      {row}
      {infoContent}
    </Popover>
  );
}
