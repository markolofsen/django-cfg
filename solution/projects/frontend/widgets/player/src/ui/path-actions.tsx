import { Check, Copy, Download, FolderOpen, Share2 } from "lucide-react";
import { Button } from "@djangocfg/ui-core";

import { useCopyFeedback } from "./use-copy-feedback";

export interface PathActionsProps {
  /**
   * What is SHOWN — already shortened for the line.
   *
   * Separate from `copyValue` on purpose: an elided path pasted into a shell
   * would not resolve, so what a reader sees and what they take are different
   * strings by design.
   */
  readonly display: string;
  /** The full path or url placed on the clipboard. */
  readonly copyValue: string;
  /**
   * What the copy button says it takes. A path and a url are copied by the
   * same control and named differently, because "copy path" on a web card
   * would describe the wrong thing.
   */
  readonly copyLabel: string;
  /**
   * Show the target in the host's file manager, selected in place.
   *
   * Absent ⇒ the button does not render. That is the case for a web page, and
   * for a machine this session cannot reveal on at all — a control that
   * appeared and then refused would be worse than its absence.
   */
  readonly onReveal?: () => void;
  /** Accessible name for the reveal button. Required whenever `onReveal` is. */
  readonly revealLabel?: string;
  /**
   * A URL that reopens this thing for someone else — copied, not navigated to.
   *
   * A VALUE, already built: only the shell knows what an address looks like,
   * and a block that assembled one would be a second author of a route. Absent
   * ⇒ no share button, which is the honest shape for anything that has no
   * address to hand out.
   */
  readonly shareUrl?: string;
  /** Accessible name for the share button. Required whenever `shareUrl` is. */
  readonly shareLabel?: string;
  /**
   * A URL whose bytes are SAVED rather than opened — an `<a download>`, so the
   * browser performs the transfer and nothing is held in memory here.
   *
   * A VALUE like `shareUrl`, for the same reason: only the caller knows which
   * address serves a copy meant for the disk. Absent ⇒ no download button,
   * which is the honest shape for anything the host does not serve.
   */
  readonly downloadURL?: string;
  /** Accessible name for the download button. Required whenever `downloadURL` is. */
  readonly downloadLabel?: string;
}

/**
 * A card's footer: where the thing is, and the acts the body cannot express.
 *
 * There is no OPEN button. A card's BODY is the open affordance — the whole
 * upper half acts, the way a messenger preview does — so a second control for
 * the same act would put two targets a few pixels apart, one of which the
 * reader was not aiming at.
 *
 * The four that remain are genuinely different acts, not variants of one.
 * Opening a `.mp3` plays it; the reader who wants the FOLDER wants to see the
 * file among its siblings, rename it, or drag it somewhere. Copy takes the
 * value, because what is on screen is elided and only the clipboard carries
 * the whole of it. SHARE takes an address instead — the path is where the file
 * sits on one machine, the link is how another person opens it. DOWNLOAD takes
 * the bytes, which is what none of the other three moves.
 *
 * Only copy is unconditional. The rest render when there is something for them
 * to do, so a footer never shows a control that would refuse.
 *
 * Icon-only, with the verb carried by the accessible name rather than a label:
 * the value is stated in the line beside them, and two words would crowd a card
 * that is already a summary.
 *
 * The shared `CopyButton` is deliberately not used: it renders "Copy"/"Copied"
 * as visible text, which is right for a command block and too heavy here. The
 * clipboard SEAM is shared — `useCopyFeedback`, the same hook that button
 * composes — so the behaviour and its confirmation window cannot drift.
 *
 * **Every label arrives as a prop.** This lives below both the chat feature and
 * the player, and those two own their copy differently — one a react-i18next
 * namespace, the other a typed dictionary. Reading either here would make this
 * package a second owner of someone else's strings.
 */
export function PathActions({
  display,
  copyValue,
  copyLabel,
  onReveal,
  revealLabel,
  shareUrl,
  shareLabel,
  downloadURL,
  downloadLabel,
}: PathActionsProps) {
  const { copied, copy } = useCopyFeedback(copyValue);
  // A SECOND instance, not a shared one: the hook holds the confirmation for
  // exactly one value, and one flag between two buttons would tick the check on
  // whichever was not pressed.
  const share = useCopyFeedback(shareUrl ?? "");

  return (
    <div className="border-border/60 mt-3 flex items-center gap-1.5 border-t pt-2.5">
      {/* `title` is the full value: the line is elided, and a reader who cannot
          see the head must still be able to read it without taking it. */}
      <p
        className="text-muted-foreground min-w-0 flex-1 truncate font-mono text-[11px]"
        title={copyValue}
      >
        {display}
      </p>
      {/* Share leads the pair: handing the thing to someone else is the act a
          reader comes to a footer for, and copy is the fallback when there is
          no address. Both put something on the clipboard, so both confirm with
          the same check rather than one of them opening a share sheet. */}
      {shareUrl !== undefined && shareUrl !== "" && (
        <Button
          type="button"
          size="icon"
          variant="ghost"
          className="size-6 shrink-0"
          aria-label={shareLabel}
          tooltip={shareLabel}
          onClick={share.copy}
        >
          {share.copied ? (
            <Check className="text-success size-3" aria-hidden />
          ) : (
            <Share2 className="size-3" aria-hidden />
          )}
        </Button>
      )}
      {/* An anchor, not a button: `download` asks the BROWSER to write the file,
          which no click handler can do without pulling the bytes into memory
          first. `asChild` keeps the icon-button shape shared with its siblings. */}
      {downloadURL !== undefined && downloadURL !== "" && (
        <Button asChild size="icon" variant="ghost" className="size-6 shrink-0" tooltip={downloadLabel}>
          <a href={downloadURL} download aria-label={downloadLabel}>
            <Download className="size-3" aria-hidden />
          </a>
        </Button>
      )}
      {onReveal !== undefined && (
        <Button
          type="button"
          size="icon"
          variant="ghost"
          className="size-6 shrink-0"
          aria-label={revealLabel}
          tooltip={revealLabel}
          onClick={onReveal}
        >
          <FolderOpen className="size-3" aria-hidden />
        </Button>
      )}
      <Button
        type="button"
        size="icon"
        variant="ghost"
        className="size-6 shrink-0"
        aria-label={copyLabel}
        tooltip={copyLabel}
        onClick={copy}
      >
        {copied ? (
          <Check className="text-success size-3" aria-hidden />
        ) : (
          <Copy className="size-3" aria-hidden />
        )}
      </Button>
    </div>
  );
}
