import { ChevronRight } from "lucide-react";
import type { ReactNode } from "react";

import { plural, useChatCopy, useChatLanguage } from "../../../i18n";

export interface ToolFoldProps {
  /** How many settled calls sit behind the counter. */
  readonly count: number;
  /** The calls, each drawn by its own renderer. */
  readonly children: ReactNode;
}

/**
 * Settled calls behind ONE counter: "3 tools used".
 *
 * A native disclosure, closed. The reader's own open/close is the element's state,
 * so nothing here can undo it; the calls inside are the ordinary tool cards, each
 * already collapsed. Which calls fold, and when, is `core/conversation/group-parts.ts`'s
 * `planFold` (this only draws the answer).
 */
export function ToolFold({ count, children }: ToolFoldProps) {
  const copy = useChatCopy().tool;
  const language = useChatLanguage();
  return (
    <details className="chat-fold">
      <summary className="chat-fold-summary">
        <span className="chat-disclosure-chevron">
          <ChevronRight className="size-3.5" aria-hidden />
        </span>
        {plural(copy.used, count, language)}
      </summary>
      <div className="chat-fold-body">{children}</div>
    </details>
  );
}
