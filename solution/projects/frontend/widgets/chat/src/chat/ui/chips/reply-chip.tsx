import { X } from "lucide-react";

import { messageCopyText } from "../message/actions";
import { useChatCopy } from "../../../i18n";
import { useComposer } from "../../composer/context";
import { useMessage } from "../../store";

/**
 * What this draft answers, above the field, with a way out.
 *
 * Self-gating like the starter rows beside it: absent target, or a target the
 * transcript no longer holds, renders nothing. A chip naming a message the
 * reader cannot see would describe a quote that will not appear.
 *
 * The quote is resolved from the STORE, not from a capability: the transcript
 * is already in this package, and asking the host to resolve an id it gave us
 * would be a second index that can disagree with the first.
 */
export function ChatReplyChip() {
  const copy = useChatCopy().composer;
  const { draft, setReplyTo } = useComposer();
  const target = useMessage(draft.replyTo ?? "");

  if (draft.replyTo === undefined || target === undefined) return null;

  return (
    <div className="chat-reply-chip flex w-full items-center gap-2 text-xs">
      <span className="bg-primary/60 h-4 w-0.5 shrink-0 rounded-full" aria-hidden />
      <span className="text-muted-foreground min-w-0 flex-1 truncate">
        {messageCopyText(target)}
      </span>
      <button
        type="button"
        onClick={() => setReplyTo(undefined)}
        aria-label={copy.replyClear}
        className="hover:bg-muted shrink-0 rounded p-0.5"
      >
        <X className="h-3 w-3" aria-hidden />
      </button>
    </div>
  );
}
