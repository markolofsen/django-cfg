import { isOtherParticipant, type ChatMessage } from "../../core/conversation/parts";
import { useCapabilities, usePreviousAuthorMatches } from "../../store";

/**
 * Another participant's bubble, on the reader's left.
 *
 * `bg-secondary` is the sender's own bubble, so this one takes `bg-muted`: two
 * stock ui-core surfaces, distinct in both themes, and no palette of our own.
 * The measure and radius match the sender's, so the two read as one conversation.
 */
export const OTHER_BUBBLE =
  "w-fit max-w-[52ch] break-words rounded-2xl bg-muted px-4 py-2.5 text-foreground";

/** A private line or a mention of this seat: an accent ring in a stock token, so it reads in both themes. */
export const HIGHLIGHT = {
  private: "ring-1 ring-primary/50",
  mention: "ring-1 ring-primary/30",
} as const;

/**
 * The speaker line above a turn: the author's name, once per run.
 *
 * Drawn from `authorId` and the host's `authors` capability. A run of turns by
 * one author carries the name on the first only, which is what
 * `usePreviousAuthorMatches` decides (a boolean, so a token arriving in the row
 * above wakes nobody). A turn without an `authorId`, or one the host gives no
 * name, wears no line, which is the case for every turn of a one-to-one chat.
 *
 * It is the default of `ChatMessageView`'s `header`, so a host that wants
 * something else still passes its own.
 */
export function MessageAuthor({ message }: { readonly message: ChatMessage }) {
  const { authors } = useCapabilities();
  const sameAsBefore = usePreviousAuthorMatches(message.id);
  if (message.authorId === undefined || sameAsBefore) return null;
  const label = authors?.labelFor(message.authorId);
  if (label === undefined) return null;
  // Over the bubble it belongs to: another participant's is on the left with it,
  // the sender's own on the right.
  const own = message.role === "user" && !isOtherParticipant(message);
  return (
    <p className={`mb-1 text-xs font-medium text-muted-foreground${own ? " text-end" : ""}`}>
      {label}
    </p>
  );
}
