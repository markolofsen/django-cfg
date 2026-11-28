import { ArrowUp, SkipForward, X } from "lucide-react";
import { useState, type ReactNode } from "react";

import type { QueuedPrompt } from "../../core/compose/queue";
import { plural, useChatCopy, useChatLanguage } from "../../../i18n";
import { useChatEvents, useQueue, useTurn } from "../../store";
import { useReplaceText, type AskReplace } from "./use-replace-text";

/**
 * Rows kept on screen. Everything past this folds behind one line.
 *
 * Three, because the composer sits at the bottom of the transcript and each row
 * eats it upward — enough to see a queue is forming, few enough that a long one
 * does not become the screen.
 */
const INLINE_LIMIT = 3;

export interface ComposerQueueProps {
  /**
   * Asked before a prompt cuts the running turn short.
   *
   * Injected for the same reason `useCopyAction` takes `write`: a dialog
   * imported here would give this package a dialog implementation, and a second
   * host no way to replace it. Absent ⇒ no confirmation and no control, because
   * an unconfirmed interrupt is the one shape this must never ship.
   *
   * Resolving false must leave the queue untouched.
   */
  readonly confirmSendNow?: () => Promise<boolean>;
  /**
   * Asked before taking a prompt back into a composer that already holds text.
   *
   * Absent ⇒ the take replaces the draft outright. Editing still works; what is
   * missing is the chance to keep both.
   */
  readonly askReplace?: AskReplace;
  readonly className?: string;
  /** The row list. Where a host puts the gap between rows. */
  readonly listClassName?: string;
  readonly itemClassName?: string;
  /** Render one queued prompt. Absent ⇒ its text, truncated by the host's CSS. */
  readonly renderItem?: (prompt: QueuedPrompt) => ReactNode;
}

/**
 * Prompts waiting for the current turn to finish.
 *
 * **Absent when empty, shown in full when short.** The queue is not a feature to
 * manage — it is a reassurance that nothing was lost, and that reassurance is
 * only delivered if the user can SEE what was taken. One or two rows is the
 * ordinary case and costs a click to open when collapsed, so they are open.
 *
 * Past `INLINE_LIMIT` the strip collapses to the summary line: the composer sits
 * at the bottom of the transcript and an unbounded list grows upward into it,
 * the same way an unbounded attachment tray once put 51 chips on screen.
 */
export function ComposerQueue({
  confirmSendNow,
  askReplace,
  className,
  listClassName,
  itemClassName,
  renderItem,
}: ComposerQueueProps) {
  const { items, count, remove, take, sendNow } = useQueue();
  const events = useChatEvents();
  const replace = useReplaceText(askReplace);
  const { isStreaming } = useTurn();
  const copy = useChatCopy().queue;
  const language = useChatLanguage();
  const [expanded, setExpanded] = useState(false);

  // Absent, not empty-and-styled: a zero-height strip still occupies a gap in
  // the composer's grid and still reads as a landmark.
  if (count === 0) return null;

  // The OVERFLOW collapses, never the whole strip.
  //
  // Hiding every row past the limit replaced the queue with a bare count — the
  // fifth prompt took the first four off screen, and the reassurance the strip
  // exists to give ("nothing was lost, here it is") went with them. The rows
  // the user can see are the feature; only the tail beyond what fits is worth
  // trading for a line.
  const overflows = count > INLINE_LIMIT;
  const visible = expanded ? items : items.slice(0, INLINE_LIMIT);
  const hidden = count - visible.length;

  // Idle needs no confirmation, so it needs no host dialog either. Only the
  // interrupting path is gated on `confirmSendNow` — an unconfirmed interrupt
  // is the one shape this must never ship.
  //
  // Shown when idle, not only while a turn runs. The queue drains itself when a
  // turn ENDS on its own, but Stop refuses to drain deliberately — so after a
  // Stop the prompt sat with no release control at all, which reads as the
  // message having been swallowed. That is the state that most needs it.
  const canSendNow = !isStreaming || confirmSendNow !== undefined;
  // The label states what the click COSTS, so it follows the same condition the
  // dialog does rather than being fixed at the interrupting wording.
  const sendNowLabel = isStreaming ? copy.sendNow : copy.send;

  const onSendNow = (id: string) => {
    // Only a RUNNING turn is lost, so only that case is worth a dialog. With
    // nothing in flight this sends immediately: asking "this will interrupt the
    // current answer" when there is no current answer describes nothing.
    if (!isStreaming) {
      sendNow(id);
      return;
    }
    // The answer is awaited before anything moves — promoting first and asking
    // after would reorder the queue for a user who then declines.
    void confirmSendNow?.().then((ok) => {
      if (ok) sendNow(id);
    });
  };

  /**
   * Take a queued prompt back for editing.
   *
   * The write is attempted FIRST and the queue entry removed only if it landed:
   * taking first would drop the prompt when the user cancels the replace. The
   * text is read from `items` rather than from `take`, because `take` is the
   * removal and must not run before the answer.
   */
  const onEdit = (id: string, text: string) => {
    void replace(text).then((written) => {
      if (!written) return;
      const prompt = items.find((item) => item.id === id);
      take(id);
      // Announced only once BOTH steps landed. This path and recall's Tab order
      // them in opposite directions on purpose, so an emit that a listener
      // acted on would invert one of them and lose the prompt on cancel.
      if (prompt !== undefined) events.emit("queue:taken", { id, draft: prompt.draft });
    });
  };

  const more = plural(copy.more, hidden, language);

  return (
    <div className={className} data-slot="composer-queue">
      <ul className={listClassName}>
        {visible.map((prompt) => (
            <li key={prompt.id} className={itemClassName}>
              {/* The text itself is the edit affordance — no third icon. Taking
                  a prompt back is what ↑ already does from the keyboard; this is
                  the same act for any row, with the mouse. */}
              <button
                type="button"
                data-action="edit"
                title={copy.edit}
                onClick={() => onEdit(prompt.id, prompt.draft.text)}
              >
                {renderItem?.(prompt) ?? <span>{prompt.draft.text}</span>}
              </button>
              {/* Icon-only: the label is a sentence and rendering it took the
                  row from the prompt. It stays as the accessible name. */}
              {canSendNow ? (
                <button
                  type="button"
                  data-action="send-now"
                  aria-label={sendNowLabel}
                  title={sendNowLabel}
                  onClick={() => onSendNow(prompt.id)}
                >
                  {/* Skip while a turn runs — it CUTS that turn, and a send
                      arrow would hide the cost. With nothing to cut it is an
                      ordinary send, and skip would name a turn that is over. */}
                  {isStreaming ? (
                    <SkipForward aria-hidden className="size-3.5" />
                  ) : (
                    <ArrowUp aria-hidden className="size-3.5" />
                  )}
                </button>
              ) : null}
              <button
                type="button"
                aria-label={copy.remove}
                title={copy.remove}
                onClick={() => remove(prompt.id)}
              >
                <X aria-hidden className="size-3.5" />
              </button>
            </li>
        ))}
      </ul>
      {/* One toggle, two labels: `hidden` is 0 once expanded, so the same
          control reads "3 more" and then "Show less". `type="button"` because
          inside the composer's <form> a bare button submits — expanding the
          queue would send the turn. */}
      {overflows ? (
        <button
          type="button"
          data-action="toggle-overflow"
          aria-expanded={expanded}
          onClick={() => setExpanded((value) => !value)}
          className="w-full text-left"
        >
          {expanded ? copy.showLess : more}
        </button>
      ) : null}
    </div>
  );
}
