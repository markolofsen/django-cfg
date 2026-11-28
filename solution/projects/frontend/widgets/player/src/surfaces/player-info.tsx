import type { ReactNode } from "react";
import { Button } from "@djangocfg/ui-core";
import { PathActions } from "../ui";
import { elidePathLine, formatBytes, formatClock } from "@djangocfg/widget-kit";
import type { MediaDetail, MediaTrack } from "../domain";

import { usePlayerCopy } from "../i18n";
import { TrackCover } from "./track-cover";

/**
 * Artwork edge in the popover.
 *
 * 64, not 96. At 96 the square was taller than the two lines of text beside it,
 * so the card carried a block of dead space to the RIGHT of the title with
 * nothing able to fill it. Sizing the artwork to its neighbour's height instead
 * makes the header one band rather than a picture with a caption stranded next
 * to it.
 */
const COVER_SIZE = 64;

/**
 * Path budget, in characters, for the FOOTER line.
 *
 * The footer spans the card's full width less two 24px buttons — ~230px inside
 * a 20rem popover — which at the 11px monospace face's ~6.6px advance is 35
 * characters. One is given back so a slightly wider face does not push the tail
 * out.
 *
 * It is a BUDGET rather than a `truncate` alone because CSS elides only the
 * tail: a path already head-elided and then tail-cut loses both of the two ends
 * that identify it, and says nothing about having done so.
 */
const PATH_MAX = 34;

export interface PlayerInfoProps {
  readonly track: MediaTrack;
  /** What is known about the file. Absent while the description is in flight. */
  readonly detail?: MediaDetail;
  /**
   * The machine's display NAME — never its id.
   *
   * Arrives as a prop because `MediaTrack.machineId` is deliberately an id (a
   * domain type must not carry a display string that goes stale) and this
   * package does not import the store. The host reads the roster and passes the
   * answer down, exactly as it does for `onOpenInFiles`.
   *
   * Undefined means the roster does not know this machine — a real state for a
   * track whose machine has left the fleet, and one the copy names.
   */
  readonly machineName?: string;
  /** Open the machine. Absent when there is nowhere to go. */
  readonly onOpenMachine?: () => void;
  /** Reveal the file in its machine's tree. */
  readonly onOpenInFiles?: () => void;
  /**
   * An address that reopens this track for someone else.
   *
   * Built by the SHELL and handed down, like every other route this package
   * touches: a player that assembled a URL would be a second author of one the
   * route registry already owns. Absent ⇒ no share control.
   */
  readonly shareUrl?: string;
}

interface Row {
  readonly key: string;
  readonly label: string;
  readonly value: ReactNode;
}

/**
 * Everything known about the playing track, in a popover.
 *
 * ## Why this is not the drawer it replaces
 *
 * The panel it supersedes was a full-width band that pushed the content column
 * up by its own height every time it opened, so reading a track's path reflowed
 * the transcript behind it. A popover is modal in TIME rather than in space: it
 * covers what is behind it and gives it straight back.
 *
 * The objection that settled the original design — that a Radix popover unmounts
 * its closed subtree and would take the `<audio>` with it — is about the ELEMENT,
 * and it only bites if the popover CONTAINS it. It does not: the element's mount
 * site is the row's frame and nothing here moves it. What is inside is text and
 * a picture, neither of which cares about being unmounted.
 *
 * ## It shows the machine's NAME, never its id
 *
 * The row used to print `b2aacd578a11b4fb477e7721bd46f912`. That string is
 * correct and useless, and the roster holds a display name for exactly this.
 *
 * ## It shortens no paths of its own
 *
 * `elidePathLine` elides by SEGMENT from the head and, at the last resort, in
 * the MIDDLE of the name — so the extension survives. CSS `text-overflow` cannot
 * do that: its only cut is the tail, which is where the extension is. This is a
 * consumer of the console's one path module, not a second author.
 */
export function PlayerInfo({
  track,
  detail,
  machineName,
  onOpenMachine,
  onOpenInFiles,
  shareUrl,
}: PlayerInfoProps) {
  const copy = usePlayerCopy();

  // data-before-jsx (`@rules`, gated by check-jsx-boundary): every row decided
  // here, composed below.
  const machineLabel = machineName ?? (track.machineId ? copy.info.machineUnknown : undefined);
  const machineValue = machineLabel === undefined
    ? undefined
    : onOpenMachine && machineName !== undefined
      ? (
        <Button
          variant="link"
          size="sm"
          elevated={false}
          onClick={onOpenMachine}
          className="h-auto justify-start p-0 text-xs font-normal"
        >
          {machineLabel}
        </Button>
      )
      : <span className="block truncate text-xs text-foreground">{machineLabel}</span>;

  // The measurements, on ONE line, separated by the same middot the chat card
  // uses. As a label/value table each of these took a full row to state four
  // characters, which is what made the card tall and its right half empty —
  // and they are all the same KIND of fact, so a reader scans them together
  // rather than looking one up.
  //
  // A zero DROPS OUT rather than printing `0:00`: the shared clock treats zero
  // as a real position, which is right for a player and wrong here, where zero
  // means nothing could measure the file.
  const facts = [
    detail?.sizeBytes ? formatBytes(detail.sizeBytes) : "",
    detail?.durationSeconds ? formatClock(detail.durationSeconds) : "",
    detail?.width && detail?.height ? `${detail.width}×${detail.height}` : "",
    detail?.codec ?? "",
  ].filter((fact) => fact !== "").join(" · ");

  // `block`, not a bare inline span. The cell around it truncates, which is
  // `overflow: hidden` — and an inline child of a hidden-overflow inline box
  // gets no layout box, so the text is on screen but measures zero: it renders,
  // and every assertion that it is VISIBLE fails.
  const plain = (value: string) => (
    <span className="block truncate text-xs text-foreground">{value}</span>
  );

  // What survives as a label/value row: the two facts that are NOT measurements
  // and cannot be read without being named. Everything else moved to the facts
  // line or to the footer.
  const candidates: readonly (Row | undefined)[] = [
    detail?.artist ? { key: "artist", label: copy.info.artist, value: plain(detail.artist) } : undefined,
    detail?.album ? { key: "album", label: copy.info.album, value: plain(detail.album) } : undefined,
    machineValue ? { key: "machine", label: copy.info.machine, value: machineValue } : undefined,
  ];
  const rows = candidates.filter((row): row is Row => row !== undefined);

  const rowNodes = rows.map((row) => (
    // Flex, not `grid-cols-[5rem_minmax(0,1fr)]`. That arbitrary value was NOT
    // generated — measured `grid-template-columns: 320px`, a single column — so
    // every label and value stacked at full width instead of pairing. A fixed
    // basis with `shrink-0` says the same thing in utilities the scanner
    // reliably emits.
    //
    // `w-20`, not `w-24`: the labels left here are short, and the value is the
    // part a reader came for.
    <div key={row.key} className="flex items-baseline gap-3">
      <span className="w-20 shrink-0 text-xs text-muted-foreground">{row.label}</span>
      <span className="min-w-0 flex-1">{row.value}</span>
    </div>
  ));

  return (
    <div className="flex flex-col" data-testid="player-info">
      {/* The artwork and the title lead, because they are what the reader
          recognises. The title is repeated from the row deliberately: the row
          truncates it to share a line with everything else, and this is the one
          place it is stated in full.
          `items-center`, not `items-start`: the text block is now shorter than
          the artwork, so aligning to the top left it hanging at the tile's
          shoulder with the rest of the square empty beside it. */}
      <div className="flex items-center gap-3">
        <TrackCover src={track.poster} kind={track.kind} size={COVER_SIZE} path={track.path} />
        <div className="flex min-w-0 flex-col gap-0.5">
          <span className="break-words text-sm font-medium">{track.title}</span>
          {facts !== "" && <span className="text-xs text-muted-foreground">{facts}</span>}
        </div>
      </div>
      {rows.length > 0 && <div className="mt-3 flex flex-col gap-1.5">{rowNodes}</div>}
      {/* The path spans the card's FULL width down here, which is the whole
          reason it moved: as a table value it had ~180px beside a label column
          and ran into the right edge. The footer also carries the two acts the
          body cannot express — take the full string, or go to the folder. */}
      {track.path !== undefined && (
        <PathActions
          display={elidePathLine(track.path, PATH_MAX)}
          copyValue={track.path}
          copyLabel={copy.info.copyPath}
          onReveal={onOpenInFiles}
          revealLabel={copy.info.revealFolder}
          shareUrl={shareUrl}
          shareLabel={copy.info.share}
        />
      )}
    </div>
  );
}
