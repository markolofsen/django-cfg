import { ArrowDown } from "lucide-react";
import type { ReactNode } from "react";

import type { ChatMessage } from "../../core";
import { fill, useChatCopy } from "../../../i18n";
import { Transcript, useHasSuggestions } from "../../primitives";
import { JumpToLatest } from "./jump-to-latest";
import { ChatMessageView } from "../message/message";
import { PendingIndicator } from "./pending";
import { TurnMark } from "./turn-mark";

export interface ChatTranscriptProps {
  /**
   * Rendered under each message's parts — the action row.
   *
   * WHICH actions exist is the host's inventory, so this stays a slot rather
   * than a labels entry.
   */
  readonly footer?: (message: ChatMessage) => ReactNode;
  /**
   * Rendered above each message, outside its frame — the speaker's name line.
   *
   * Passed through to the row, which places it: only a ROOM has several
   * speakers to tell apart, and a host with one correspondent passes nothing.
   */
  readonly header?: (message: ChatMessage) => ReactNode;
  /**
   * Replaces the default empty-room line, for a host that has something truer
   * to say about THIS room than "no messages yet".
   *
   * A slot rather than a labels entry: the host renders a node, not a string,
   * and only the host knows the facts its room carries. The primitive still
   * owns WHEN an empty state may paint — a pending fetch and an in-flight first
   * turn both suppress it — so a host node cannot claim a room is empty while
   * history is still loading.
   */
  readonly empty?: ReactNode;
  readonly className?: string;
}

/**
 * The transcript, assembled.
 *
 * ONE assembly, for the reason `ChatComposer` is one: the pending indicator and
 * the jump-to-latest control are render props on the primitive, so a host that
 * composes it by hand ships a transcript missing whichever it forgot — and
 * nothing fails, the feature is simply absent. That is not hypothetical:
 * `jumpToLatest` existed on the primitive with no consumer at all until this
 * assembly filled it.
 *
 * A host needing a different shape still drops to `<Transcript>` and keeps
 * every behaviour; this is the default, not the only door.
 */
export function ChatTranscript({
  footer,
  header,
  empty: hostEmpty,
  className,
}: ChatTranscriptProps) {
  const copy = useChatCopy().transcript;
  const hasSuggestions = useHasSuggestions();
  // A FALLBACK, not a caption. Starter rows above the composer already say the
  // room is empty and name what to do, so the line only earns its place when
  // there are none — a room with no suggestion capability, or one whose filters
  // excluded everything. `null` rather than an empty node: the primitive falls
  // back to rendering the transcript, not a blank box.
  //
  // A host node wins over both. It is checked for `undefined` rather than
  // truthiness because a host that HAS the facts and finds nothing to say
  // returns null, and that must fall through to the default line rather than
  // paint a blank pane.
  //
  // Centred in the pane rather than set at the top-left. A single muted line
  // pinned to a corner of an otherwise empty window reads as a layout that
  // failed, not as an answer; the sentence is all this state has, so it stands
  // where the eye already is. `min-h-full` and not `h-full`: the box must be
  // free to grow with a translation that wraps.
  const fallback = hasSuggestions ? null : (
    <div className="flex min-h-full items-center justify-center p-8">
      <p className="text-muted-foreground text-center text-sm text-balance">{copy.empty}</p>
    </div>
  );
  const empty = hostEmpty === undefined ? fallback : hostEmpty;

  // The announcer takes a fixed pair. Built here rather than inline in JSX so
  // the object identity is stable per render pass, matching rule 5.
  const announce = { streaming: copy.announceStreaming, complete: copy.announceComplete };

  return (
    <Transcript
      /*
        The SCROLLER spans the pane; the reading column caps its CONTENTS.
        Capping the scroller itself would pull the scrollbar into the middle of
        the window, away from the edge where a pointer expects it.

        `chat-surface` carries the type scale. The width is `chat-column`, and
        it belongs on the CONTENT wrapper inside — the primitive puts it there,
        because the rule caps direct children and the rows are that element's
        children. Here it would cap the wrapper alone and cost nothing.

        `pb-10`: without it the last line ends a few pixels above the composer
        and the two read as one surface. On the SCROLLER, not the last row — a
        margin there is eaten by the sticky-bottom write.
      */
      className={`chat-surface min-h-0 ${className ?? ""}`}
      empty={empty}
      label={copy.log}
      announce={announce}
      // Shown only while scrolled away — the transcript owns that gate, so this
      // never decides its own visibility.
      jumpToLatest={({ onClick, missed }) => (
        <JumpToLatest
          onClick={onClick}
          missed={missed}
          label={copy.jumpToLatest}
          icon={<ArrowDown className="size-4" aria-hidden />}
        />
      )}
      // The answer will land here, so the promise of one belongs here too — not
      // on the Stop button in the far corner, which is otherwise the only
      // evidence a sent turn produced.
      //
      // It spans the WHOLE turn. While `waiting` it carries the label and the
      // elapsed counter, because nothing else is on screen to explain the pause;
      // once text is `working` the answer speaks for itself, so the row drops to
      // the mark alone and trails the reply instead of captioning it.
      pending={(activity) =>
        activity === "waiting" ? (
          <PendingIndicator
            // Body size, not `text-sm`. This line stands exactly where the reply
            // will appear, so a smaller one announces the answer in a different
            // voice from the answer — and Tailwind's fixed 14px ignores the chat
            // scale entirely, so it drifted further the moment the body grew.
            className="text-muted-foreground flex items-center gap-2 py-3 text-[length:var(--chat-text)]"
            label={copy.thinking}
            elapsed={(seconds) => fill(copy.thinkingElapsed, { seconds })}
          />
        ) : (
          <div className="text-muted-foreground py-1">
            <TurnMark state="working" />
          </div>
        )
      }
    >
      {/*
        The styled row, not the headless `<Message>`: it carries the bubble
        decision — user turns get one, replies stay open text — and declares the
        role once so descendants read it through `group-[.is-user]:` instead of
        taking a `from` prop each.
      */}
      {/* No vertical padding: the transcript's own `gap` is the one rhythm
          between messages. Padding here would add to it unevenly, since a row's
          height already varies with the optional speaker line. */}
      {(id) => <ChatMessageView id={id} footer={footer} header={header} />}
    </Transcript>
  );
}
