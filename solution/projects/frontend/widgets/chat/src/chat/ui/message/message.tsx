import { cn } from "@djangocfg/ui-core/lib";
import { formatDayOfMonth } from "@djangocfg/widget-kit";
import { MessageQuote } from "./quote";
import { HIGHLIGHT, MessageAuthor, OTHER_BUBBLE } from "./author";

import { isOtherParticipant, type ChatMessage } from "../../core/conversation/parts";
import { useChatCopy } from "../../../i18n";
import { Message as HeadlessMessage } from "../../primitives";
import { usePreviousMessageTime } from "../../store";
import { dayHeadingFor } from "../../utils";
import { CollapsibleRow } from "./collapsible-row";
import { DayDivider } from "./day-divider";

/**
 * The styled message row: a bubble for the user, open text for the reply.
 *
 * That asymmetry is the whole design, and it is Vercel's — verified against
 * `@sources/vercel-ai-elements/.../message.tsx`, which bubbles `is-user` only
 * and leaves `is-assistant` as bare `text-foreground`. It is right for a reason
 * worth stating: a bubble is a frame, and a frame around a long reply that
 * contains code, a diff and a plan competes with the content it holds. The user
 * turn is short and needs to be findable while scanning; the reply is the
 * product and gets the page.
 *
 * Role is declared ONCE, on the wrapper, as `is-user` / `is-assistant`, and
 * every descendant reads it through `group-[.is-user]:`. The alternative —
 * passing `from` down to each styled piece — is the shape that grows a prop per
 * level, which is exactly what the 83-prop predecessor did.
 *
 * We differ from Vercel in three places, each measured rather than preferred:
 *
 * 1. **No `from` prop.** Their `<Message from={...}>` exists because their
 *    message is a prop; ours comes from the store and already carries `role`.
 *    A prop here would be a second writer for a value we hold.
 * 2. **The measure is on the reply TEXT, not the container.** Long prose needs
 *    a line length near 72ch to stay readable, but a diff, a plan or a table
 *    needs the full column. Capping the container would cap the widgets too, so
 *    the cap lives on `MessageProse`, which a part renderer wraps around text
 *    and around nothing else.
 * 3. **`min-w-0` + `break-words` on the bubble.** A pasted absolute path is one
 *    unbreakable token; without these it distends the flex column and pushes
 *    the transcript sideways. Users paste paths constantly.
 * 4. **The bubble carries its own cap**, in `ch` — the reply's unit, so the two
 *    measures are comparable. `%` would re-couple it to the container and `px`
 *    breaks when the host resizes the chat text.
 */

export interface ChatMessageViewProps {
  readonly id: string;
  readonly className?: string;
  /**
   * Rendered under the parts, inside the frame — the action row's seam.
   *
   * A slot rather than an `actions` prop threaded through: WHICH actions exist
   * is the host's, and passing them through here would make this component a
   * courier for a list it never reads. The host receives the message it is
   * acting on, which is everything an action needs to be built.
   */
  readonly footer?: (message: ChatMessage) => React.ReactNode;
  /**
   * Rendered ABOVE the row, outside the frame — the speaker's name line.
   *
   * Above and outside deliberately: attribution is a caption on a turn, not a
   * change to the turn's frame. A room needs to say who is talking; a
   * one-to-one chat's speaker is the contact on screen, so its host passes
   * nothing and the row is byte-identical to before this slot existed.
   *
   * A slot for the same reason `footer` is one: WHO a speaker is resolves
   * against a roster this package does not hold, and returning null for a turn
   * that wears no line is the host's call.
   */
  readonly header?: (message: ChatMessage) => React.ReactNode;
}

/**
 * A row in the transcript, resolved from the store by id.
 *
 * `<Transcript>{(id) => <ChatMessageView id={id} />}</Transcript>` is the whole
 * wiring. The headless `<Message>` does the lookup and the memoization; this
 * adds the frame.
 */
export function ChatMessageView({ id, className, footer, header }: ChatMessageViewProps) {
  return (
    <HeadlessMessage id={id}>
      {(message, parts) => (
        <>
          <MessageDayDivider id={id} createdAt={message.createdAt} />
          {header === undefined ? <MessageAuthor message={message} /> : header(message)}
          {/* Above the row, with the speaker line: a quote says what this turn
              answers, which is context for the row rather than part of it. */}
          <MessageQuote message={message} />
          <CollapsibleRow
            message={message}
            parts={parts}
            className={className}
            footer={footer?.(message)}
          />
        </>
      )}
    </HeadlessMessage>
  );
}

/**
 * The day heading above a row, when that row opens a new calendar day.
 *
 * Rendered from INSIDE the row rather than from the transcript's map: the list
 * subscribes to ids alone so a token re-renders one component, and reading
 * every message's time up there would re-render the whole list per token.
 *
 * The clock is read once per row and not memoized on purpose — a transcript
 * open across midnight relabels on its next render, which is the honest answer
 * and costs nothing next to what a timer would.
 */
function MessageDayDivider({ id, createdAt }: { id: string; createdAt: number }) {
  const copy = useChatCopy().transcript;
  const previous = usePreviousMessageTime(id);
  const heading = dayHeadingFor(createdAt, previous, Date.now());
  if (heading === undefined) return null;
  const label =
    heading === "today"
      ? copy.today
      : heading === "yesterday"
        ? copy.yesterday
        : formatDayOfMonth(createdAt);
  // `sv-SE` is ISO-8601 by locale, which is what `<time datetime>` requires —
  // and it is a FORMAT choice, never the reader's locale.
  const dateTime = new Date(createdAt).toLocaleDateString("sv-SE");
  return <DayDivider label={label} dateTime={dateTime} />;
}

export interface ChatMessageFrameProps {
  readonly message: ChatMessage;
  readonly className?: string;
  readonly children: React.ReactNode;
  /**
   * Rendered after the bubble, inside the group.
   *
   * Inside the group because the action row reveals on `group-hover`; outside
   * the bubble because a control sitting on the user's background would read as
   * part of what they said, and because the bubble's `select-text` would put a
   * button's label into a copied turn.
   */
  readonly footer?: React.ReactNode;
  /**
   * The footer's opposite end — a second POSITION, not a second slot's worth of
   * chrome.
   *
   * One position forces everything into one row in source order, so a control
   * that belongs beside the actions rather than after them has nowhere to go.
   * Taken from the reference's `MessageToolbar`, which is a `justify-between`
   * row the host fills from either end.
   *
   * Absent by default, and when absent the footer keeps its own alignment
   * rather than being centred by an empty sibling.
   */
  readonly footerEnd?: React.ReactNode;
}

/**
 * The frame around already-rendered parts.
 *
 * Split from the lookup because a subagent's messages live inside a tool part,
 * not in the store — the same reason `MessageContent` exists beside `Message`
 * one layer down. A nested thread gets the same bubble without a second,
 * subtly-different implementation.
 *
 * `system` shares the assistant's open-text treatment: it is not the user
 * speaking, and giving it a third visual identity would ask the reader to learn
 * one more thing for a role they see rarely.
 */
export function ChatMessageFrame({
  message,
  className,
  children,
  footer,
  footerEnd,
}: ChatMessageFrameProps) {
  const isOther = isOtherParticipant(message);
  const isUser = message.role === "user" && !isOther;
  const failed = message.status.state === "failed";
  const hasMedia = message.parts.some((part) => part.type === "attachment" && part.attachment.kind === "image" && part.attachment.url !== "");
  const hasToolbar = footer !== undefined || footerEnd !== undefined;
  // Both ends filled: hold them apart. One end: send it to the speaker's side. It cannot be left unset: the 28px footer box
  // moves nothing inside itself, the toolbar row places it, and `normal` is the left edge (a user's copy control sat under the far side).
  const bothEnds = footer !== undefined && footerEnd !== undefined;
  const toolbarJustify = bothEnds
    ? "justify-between"
    : isUser
      ? "justify-end"
      : "justify-start";

  return (
    <div
      // Jump-to-message anchor: a data attribute, since ids are document-global (see `ChatSurfaces.revealMessage`).
      data-message-id={message.id}
      data-role={message.role}
      data-status={message.status.state}
      className={cn(
        // `select-none` here, `select-text` on each part below. Both halves are
        // load-bearing: the padding and the gap BETWEEN two messages must not
        // be selectable, or a drag bridges one turn into the next and a copy
        // returns two speakers fused into one block. Putting `select-text` on
        // the bubble instead makes its own padding selectable and fuses them
        // exactly the same way.
        "group flex w-full max-w-full select-none flex-col gap-2",
        isUser ? "is-user items-end" : cn(isOther ? "is-other" : "is-assistant", "items-start"),
        className,
      )}
    >
      <div
        className={cn(
          // min-w-0 is what lets a long token wrap instead of widening the row.
          //
          // NO `text-sm` here, deliberately. It looks like a harmless default
          // and is not: `sm` is the CONTROL scale, and setting it on the row
          // breaks inheritance for everything below — so a host that sizes its
          // chat surface finds the transcript ignoring it while the composer
          // obeys, which is the two-scales defect the size token exists to
          // prevent. Measured: surface 15px, this row 12px, in the same chat.
          //
          // The row inherits. A host that wants a size sets it on the surface,
          // once, for both.
          "flex min-w-0 max-w-full flex-col gap-2",
          // Selection opts back in on the CONTENT column, and it is `*:` — every
          // direct child, whatever the registry rendered — rather than a list of
          // known branches. The archive's regression is the reason: for a long
          // time only its markdown leaf opted in, so tool calls, their output,
          // typed blocks and attachments could not be copied AT ALL. A registry
          // makes that failure certain, because the parts are not ours to
          // enumerate. Containment is unchanged: the column's own padding and
          // the `gap-2` between parts stay dead, so a drag still cannot bridge
          // two messages.
          "[&>*]:select-text",
          // `w-fit` keeps a short turn short, the cap bounds the long end —
          // either alone gets one of the two shapes wrong. Narrower than the
          // reply's 72ch, so gutter separates ask from answer at any viewport.
          "group-[.is-user]:w-fit group-[.is-user]:max-w-[52ch]",
          "group-[.is-user]:rounded-2xl group-[.is-user]:bg-secondary",
          // Pictures hug the bubble (4px, as in Telegram); text parts take their own inset.
          hasMedia
            ? "group-[.is-user]:p-1 group-[.is-user]:[&>*:not([data-media])]:px-3 group-[.is-user]:[&>*:not([data-media])]:py-1"
            : "group-[.is-user]:px-4 group-[.is-user]:py-2.5",
          "group-[.is-user]:text-secondary-foreground",
          "group-[.is-user]:[overflow-wrap:anywhere]", // lowers min-content, which `w-fit` sizes from
          // The reply is not a bubble: full column, page text colour.
          "group-[.is-assistant]:w-full group-[.is-assistant]:text-foreground",
          isOther && OTHER_BUBBLE, message.highlight && HIGHLIGHT[message.highlight],
          failed && "border border-destructive/40 bg-destructive/5 px-3 py-2",
        )}
      >
        {children}
        {/* The failure reason lives on the status, not in a part: without this a turn that failed before any text is an empty red box. */}
        {message.status.state === "failed" && message.status.message ? <p role="alert" className="text-sm text-destructive">{message.status.message}</p> : null}
      </div>
      {/*
        The toolbar sits in flow under the bubble, and most of the height it
        takes is given back here rather than by floating it: an overlaid row
        does not read as belonging to the message it acts on.

        `-mb-2` (8px), NOT the toolbar's full 28px. Giving back the whole height
        made the row's box end ABOVE the toolbar, so the transcript's gap was
        measured from there and the toolbar overlapped the next message by 2px
        wherever no speaker line stood between them — closer to the turn it does
        not act on than to the one it does. 8px is the largest give-back that
        keeps every toolbar nearer its own text; measured, not chosen.

        `gap-2` above adds 8px between the bubble and the toolbar, which stays —
        the toolbar must not touch the bubble.
      */}
      {hasToolbar && (
        <div className={cn("-mb-2 flex w-full items-center gap-4", toolbarJustify)}>
          {footer}
          {footerEnd}
        </div>
      )}
    </div>
  );
}

/**
 * The readable measure for model prose.
 *
 * ~72ch, applied by the TEXT part renderer — never by the row. A plan, a diff
 * or a table registered for its own part type keeps the full column, because
 * truncating a table to prose width makes it unreadable in a different way.
 *
 * `max-w-none` on the user side: a bubble is already narrow, and a second cap
 * inside it produces a ragged short column against a wide bubble edge.
 */
export function MessageProse({ children, className }: {
  readonly children: React.ReactNode;
  readonly className?: string;
}) {
  return (
    <div className={cn("max-w-[72ch] group-[.is-user]:max-w-none", className)}>{children}</div>
  );
}
