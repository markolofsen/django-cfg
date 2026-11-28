import { Play } from "lucide-react";
import { Button } from "@djangocfg/ui-core";
import type { MediaTrack } from "../domain";

import { usePlayerCopy } from "../i18n";
import { TrackCover } from "./track-cover";

export interface MediaButtonProps {
  readonly track: MediaTrack;
  /** True when this file is the one the player currently holds. */
  readonly active: boolean;
  /** Play this file. The host loads it into the store and starts it. */
  readonly onPlay: () => void;
}

/**
 * One playable file, as a REMOTE CONTROL for the one player.
 *
 * Two surfaces use it and **neither mounts a media element**: the chat
 * transcript, as the `audio`/`video` block renderer, and the Files viewer. It is
 * the shared "load this into the player" affordance, which is why it is named
 * for what it IS rather than for where it first appeared.
 *
 * Why not the kit's `AudioBlock`/`VideoBlock`: those each mount a real player. A
 * transcript can hold several, and every one that mounts is another owner of
 * "what is playing" — two audible at once, each with its own notion of current,
 * and all of them dying the moment the reader navigates away
 * (`@rules/general/architecture-and-ownership.md`: two owners create races; here the race
 * makes noise).
 *
 * ## Video has no exception here, and that is the change
 *
 * The card this replaces mounted a real video player while its file was the
 * active track. The reason was sound: a video played from a corner is a voice
 * with nothing to look at, so the frame had to live where the message was.
 *
 * That reasoning was right, and it is not overturned — it is **answered**. The
 * player now has a stage, so a video has somewhere to be seen that is not a
 * message bubble. With that in place the exception costs more than it buys: it
 * was the one path by which a transcript owned an element, and therefore the one
 * by which navigating away killed a video.
 *
 * So every kind is a remote control, and the transcript mounts nothing.
 */
export function MediaButton({ track, active, onPlay }: MediaButtonProps) {
  const copy = usePlayerCopy();

  // The containing folder answers "which of my copies is this?" and nothing
  // more, which is the only question a label this size can honestly answer. No
  // full path and no machine id: the card sits inches from the request that
  // produced it ("play X"), so restating where X lives is noise — and a raw
  // 32-char machine id was the worst of it. The location stays one click away
  // through the dock's title.
  const folder = track.path ? parentFolderLabel(track.path) : "";

  // Every decision is made here; the JSX below only composes already-prepared
  // nodes (`@rules` data-before-jsx, gated by `check-jsx-boundary.mjs`).
  //
  // The artwork LEADS, the shape every music app uses, and Play sits ON it
  // rather than beside it: overlaying keeps one target instead of two and frees
  // the row for title and folder.
  // With artwork the overlay DIMS it and Play reads against the darkened
  // picture. With none, the tile below is already a glyph — a translucent wash
  // leaves two symbols competing in one 40px square, which is what a voice note
  // (no embedded art) showed. There Play REPLACES the glyph: opaque ground, one
  // symbol at a time.
  const hasArtwork = track.poster !== undefined && track.poster !== "";
  const overlayClass = hasArtwork
    ? "bg-black/35 text-white"
    : "bg-muted text-foreground";

  const coverNode = (
    <span className="relative shrink-0">
      <TrackCover src={track.poster} kind={track.kind} size={40} path={track.path} />
      <span
        aria-hidden
        className={`absolute inset-0 grid place-items-center rounded-md opacity-0 transition-opacity group-hover:opacity-100 ${overlayClass}`}
      >
        <Play className="size-4" />
      </span>
    </span>
  );

  const folderNode = folder
    ? <span className="truncate text-xs text-muted-foreground">{folder}</span>
    : null;

  const activeNode = active
    ? <span className="shrink-0 text-xs text-muted-foreground">{copy.dock.label}</span>
    : null;

  return (
    <Button
      variant="outline"
      elevated={false}
      onClick={onPlay}
      aria-pressed={active}
      className="group h-auto w-full justify-start gap-3 px-3 py-2 text-left font-normal"
    >
      {coverNode}
      <span className="flex min-w-0 flex-1 flex-col">
        <span className="truncate text-sm font-medium">{track.title}</span>
        {folderNode}
      </span>
      {activeNode}
    </Button>
  );
}

/**
 * The containing folder, shortened for a one-line label: the last folder only.
 *
 * A full absolute path is what made the player bar unreadable — half its width
 * was `/Users/<name>/Desktop/archived/Personal/laptop old-mac (backup)/…`.
 */
export function parentFolderLabel(path: string): string {
  const parts = path.split(/[/\\]+/).filter(Boolean);
  if (parts.length < 2) return "";
  return parts[parts.length - 2] ?? "";
}
