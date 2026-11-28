import { isOtherParticipant, type ChatMessage } from "../../core/conversation/parts";
import { messageCopyText } from "./actions";
import { useChatCopy } from "../../../i18n";
import { useChatSurfaces, useMessage } from "../../store";

/**
 * The message a turn answers, above its own text.
 *
 * Renders nothing when this turn answers nothing, or when the answered message
 * is not in the loaded transcript — a quote naming a row the reader cannot
 * scroll to would describe something that is not there. History is paged, so
 * that is an ordinary state rather than an error.
 *
 * Resolved from the store, like the composer's chip: one index, so the quote a
 * sender saw and the quote a reader sees cannot disagree.
 */
export function MessageQuote({ message }: { readonly message: ChatMessage }) {
  const target = useMessage(message.replyTo ?? "");
  const surfaces = useChatSurfaces();
  const copy = useChatCopy().message;
  if (message.replyTo === undefined || target === undefined) return null;

  const quoted = message.replyTo;
  return (
    <button
      type="button"
      onClick={() => surfaces?.revealMessage(quoted)}
      aria-label={copy.jumpToQuoted}
      // `w-fit` with a cap, not `w-full`: the quote belongs to ONE bubble, and a
      // full-column bar above a short right-aligned turn reads as a divider for
      // the whole transcript. The cap matches the user bubble's own measure so a
      // long quote wraps where the bubble would.
      //
      // `ms-auto` on a user turn puts it over the bubble it belongs to. The row
      // below is aligned by the frame's own `items-end`, which this element sits
      // outside of, so it places itself.
      className={`chat-quote hover:bg-muted/50 mb-1 flex w-fit max-w-[52ch] items-center gap-2 rounded px-1 py-0.5 text-left text-xs${
        message.role === "user" && !isOtherParticipant(message) ? " ms-auto" : ""
      }`}
    >
      <span className="bg-primary/60 h-4 w-0.5 shrink-0 rounded-full" aria-hidden />
      <span className="text-muted-foreground min-w-0 truncate">
        {messageCopyText(target)}
      </span>
    </button>
  );
}
