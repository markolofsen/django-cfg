import { memo, useCallback, useEffect, useRef, useState, type ReactNode } from "react";

import {
  useChatSurfaces,
  useHistoryLoaded,
  useMessage,
  useMessageIds,
  useTurn,
} from "../../store";
import { useMissedCount } from "./use-missed-count";
import { useReturnOnSend } from "./use-return-on-send";
import { useRovingFocus } from "./use-roving-focus";
import { useHoldBottom } from "./use-hold-bottom";
import { useStickToBottom } from "./use-stick-to-bottom";
import { useTurnActivity, type TurnActivity } from "./use-turn-activity";

export interface TranscriptProps {
  /** Render one message. Called with the id; the row reads the message itself. */
  readonly children: (id: string) => ReactNode;
  /** Shown when there are no messages — an empty transcript is a real state. */
  readonly empty?: ReactNode;
  readonly className?: string;
  /**
   * The accessible name of the log. Copy is the host's — no locales here.
   *
   * Without it `role="log"` is an unnamed landmark: a screen reader user moving
   * between regions hears "log" with nothing to distinguish it.
   */
  readonly label?: string;
  /**
   * What to say when a reply starts and when it ends — the ONLY two strings a
   * screen reader hears per turn.
   *
   * Absent means no announcements at all, which is the correct default for a
   * host that already announces elsewhere: a second live region would make
   * every reply be read twice.
   */
  readonly announce?: {
    readonly streaming: string;
    readonly complete: string;
  };
  /**
   * Rendered when the user has scrolled away from the bottom, with a callback
   * that returns them to it.
   *
   * A render prop rather than a built-in button, because the control is styled
   * and worded by the host — and because a transcript that decides its own
   * chrome is how a primitive turns back into 83 props.
   *
   * `missed` is how many replies arrived since the reader left, or **null when
   * there is nothing honest to show** — a fresh unpin, or a conversation opened
   * already scrolled up. Null and 0 are different states; only a real arrival
   * deserves a number, so a host must render no badge rather than an empty one.
   */
  readonly jumpToLatest?: (props: {
    readonly onClick: () => void;
    readonly missed: number | null;
  }) => ReactNode;
  /**
   * Rendered after the last row for as long as a turn is in flight, given what
   * that turn is currently doing.
   *
   * `waiting` — sent, nothing back yet. `working` — text is arriving. It ends at
   * turn-end, so a host can carry one indicator across both phases instead of
   * showing something during the silence and nothing during the answer.
   *
   * In the transcript rather than beside the composer because that is where the
   * answer will appear, so the promise of one belongs there too. It also rides
   * inside the scroll container, which is what makes the autoscroll treat it as
   * new content and keep the view pinned to the bottom.
   *
   * Never a message: it has no id and never enters the store, so it cannot leak
   * into stored history as a message nobody sent.
   *
   * ONE slot rather than one per phase, and ONE owner rather than a decision
   * repeated in every row: a message that reports its own completion reports it
   * forever, so the indicator stacks up once per reply on a single screen.
   *
   * A render prop, like `jumpToLatest`, because the copy and the chrome are the
   * host's — this package carries no locales.
   */
  readonly pending?: (activity: TurnActivity) => ReactNode;
}

/**
 * The message list.
 *
 * Not virtualized, deliberately. Virtualization fights streaming (heights
 * change on every token), autoscroll, and find-in-page, and the transcripts
 * a chat room shows are hundreds of messages, not tens of thousands. The
 * measurement comes first: if a real transcript stutters, that is when this
 * decision gets revisited — `@rules/architecture.md`.
 */
export function Transcript({
  children,
  empty,
  className,
  label,
  announce,
  jumpToLatest,
  pending,
}: TranscriptProps) {
  const ids = useMessageIds();
  const historyLoaded = useHistoryLoaded();
  const activity = useTurnActivity();
  const { ref, contentRef, onScroll, isPinned, scrollToBottom, holdBottom } = useStickToBottom(ids.length);
  const hold = useHoldBottom({ hold: holdBottom });
  const missed = useMissedCount(ids, isPinned);
  useReturnOnSend(ids, scrollToBottom);
  const roving = useRovingFocus(ids.length);
  const transition = useTurnAnnouncement(announce);
  const waiting = activity !== null && pending !== undefined ? pending(activity) : null;
  const surfaces = useChatSurfaces();
  // Two owners of one node: the scroll machinery needs it, and a host needs it
  // to scope a selection to the conversation. Both callbacks, so this composes
  // without either learning about the other.
  const attach = useCallback(
    (node: HTMLDivElement | null) => {
      ref(node);
      hold(node);
      surfaces?.registerTranscript(node);
    },
    [ref, hold, surfaces],
  );

  // Two things suppress the empty state, both because it would be a LIE.
  //
  // `waiting`: a first turn sent into a fresh room is not an empty transcript,
  // and "no messages yet" under a prompt the user just sent says the opposite
  // of what happened.
  //
  // `historyLoaded`: an unanswered fetch is not an empty room. Without it a
  // conversation with 90 replies opened on "no messages yet" for the duration
  // of the load.
  if (ids.length === 0 && empty !== undefined && waiting === null && historyLoaded) {
    return <div className={className}>{empty}</div>;
  }

  return (
    <>
      {/*
        Three elements: outer clips, scroller fills it, content grows.

        Merging the outer two paints the scroller from its first frame, which is
        at the TOP — the library cannot know the bottom before it measures. Cost
        a ~33ms flash of old history on entering every room.
      */}
      <div className={`grid overflow-hidden ${className ?? ""}`}>
      <div
        ref={attach}
        onScroll={onScroll}
        onKeyDown={roving.onKeyDown}
        className="h-full overflow-y-auto"
        // `role="log"` names what this is and implies `aria-relevant="additions"`
        // — additions only, never text mutations.
        //
        // Never spell `aria-relevant="additions text"` here: `text` asks the
        // screen reader to announce changes to text NODES inside the region,
        // and a streamed reply rewrites its text node on every delta, so the
        // whole answer is read out token by token. None of the surveyed
        // libraries sets `aria-relevant` at all — the announcement belongs on a
        // separate node, below.
        role="log"
        aria-label={label}
        aria-live="polite"
      >
        {/*
          The measured element, and the one the reading column now caps.

          The library needs a child whose height IS the content's, separate from
          the scroller whose height is the viewport's — that difference is what
          it observes. `chat-column` moves here with it: the rule caps direct
          children, and the rows are this element's children now.
        */}
        {/* `pb-10` on the CONTENT, not the scroller: it must be part of the
            measured height, or the follow stops a gap short of the composer.
            The right inset keeps text off the scrollbar, which runs at the
            pane's own edge; the host sizes it, so a phone can widen it to match
            its other margins. */}
        {/* The rhythm between messages is declared HERE, on the element that
            owns the rows. Without it the only thing parting two rows is
            whatever they happen to render: a speaker line is omitted for a
            consecutive same-author turn, so those pairs sat flush while their
            neighbours kept the line's 28px. Spacing that depends on optional
            content is not spacing. */}
        <div ref={contentRef} className="chat-column chat-inset-r flex flex-col gap-4 pt-4 pb-10">
          {ids.map((id, index) => (
            <div key={id} {...roving.itemProps(index)}>
              <MessageRow id={id}>{children}</MessageRow>
            </div>
          ))}
          {waiting}
        </div>
      </div>
      </div>
      {/*
        Anchored to the SCROLLER's bottom, not the chat's: the chat's last grid
        row is the composer, so a control positioned against it lands on top of
        the input. `sticky` inside the scroll container would ride the content;
        this sits in a zero-height strip at the scroller's own lower edge.

        `pointer-events-none` on the strip so it never eats a click aimed at the
        last message; the control inside opts back in.
      */}
      {!isPinned && jumpToLatest !== undefined && (
        <div className="pointer-events-none relative h-0 [&>*]:pointer-events-auto">
          {jumpToLatest({ onClick: scrollToBottom, missed })}
        </div>
      )}
      <TurnAnnouncer text={transition} />
    </>
  );
}

/**
 * The two words a screen reader hears per turn.
 *
 * Only TRANSITIONS — never the streamed content — so this can never spam.
 * `role="status"` is an implicit polite, atomic live region: atomic means the
 * whole node is re-read on change, which is right for a one-line status and
 * wrong for a transcript.
 *
 * Always rendered, even when empty: a live region created at the moment of the
 * event is not announced, because assistive tech must have been observing the
 * node beforehand.
 */
function TurnAnnouncer({ text }: { readonly text: string }) {
  return (
    <div
      role="status"
      style={{
        position: "absolute",
        width: 1,
        height: 1,
        margin: -1,
        padding: 0,
        overflow: "hidden",
        // `clip` over `display:none` or `visibility:hidden`: those two remove
        // the node from the accessibility tree entirely, taking the
        // announcement with them.
        clip: "rect(0 0 0 0)",
        whiteSpace: "nowrap",
        border: 0,
      }}
    >
      {text}
    </div>
  );
}

/** The transition string for the current turn, or "" when there is nothing to say. */
function useTurnAnnouncement(announce: TranscriptProps["announce"]): string {
  const { isStreaming } = useTurn();
  const [text, setText] = useState("");
  const wasStreaming = useRef(false);

  useEffect(() => {
    const was = wasStreaming.current;
    wasStreaming.current = isStreaming;
    // Only on a CHANGE. Re-running on every render would re-announce, and an
    // atomic region re-reads its whole contents each time it is written.
    if (announce === undefined || was === isStreaming) return;
    // "complete" is not announced on mount — `was` starts false, so the first
    // transition it can report is false→true.
    setText(isStreaming ? announce.streaming : announce.complete);
  }, [announce, isStreaming]);

  return text;
}

interface MessageRowProps {
  readonly id: string;
  readonly children: (id: string) => ReactNode;
}

/**
 * One row, memoized on its id.
 *
 * `useMessage(id)` subscribes to that message alone, so a token arriving in the
 * last row re-renders one component. Without this pair the list re-renders per
 * token and the cost grows with transcript length — the stutter that reads as
 * "the chat is laggy" rather than as a rendering bug.
 */
const MessageRow = memo(function MessageRow({ id, children }: MessageRowProps) {
  const message = useMessage(id);
  if (message === undefined) return null;
  return <>{children(id)}</>;
});
