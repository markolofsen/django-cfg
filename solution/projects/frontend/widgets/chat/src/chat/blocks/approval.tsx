import { Check, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@djangocfg/ui-core/components";

import { useChatCopy } from "../../i18n";
import type { ApprovalPayload } from "./payload";
import { BLOCK_CARD } from "./style";

export interface ApprovalBlockProps {
  readonly data: ApprovalPayload;
  /** `true` for Apply, `false` for Dismiss. */
  readonly onDecide: (apply: boolean) => void;
  readonly settled?: boolean;
}

/** A proposed change waiting for a decision: the summary, the before → after list, Apply and Dismiss. Nothing happens by rendering. */
export function ApprovalBlock({ data, onDecide, settled = false }: ApprovalBlockProps) {
  const copy = useChatCopy().blocks;
  const [state, setState] = useState<"open" | "applied" | "dismissed">("open");
  const decide = (apply: boolean) => {
    setState(apply ? "applied" : "dismissed");
    onDecide(apply);
  };
  const open = state === "open" && !settled;

  return (
    <div className={BLOCK_CARD} data-block="approval" data-state={state}>
      <p className="font-medium">{data.summary}</p>
      {data.changes.length > 0 ? (
        <ul className="mt-2 space-y-1 text-xs">
          {data.changes.map((change) => (
            <li key={change.path} className="flex flex-wrap items-baseline gap-x-2">
              <code className="text-muted-foreground">{change.path}</code>
              {change.from ? <span className="text-muted-foreground line-through">{change.from}</span> : null}
              {change.from ? <span aria-hidden="true" className="text-muted-foreground">→</span> : null}
              <span>{change.to}</span>
            </li>
          ))}
        </ul>
      ) : null}
      <div className="mt-3 flex items-center gap-2">
        {open ? (
          <>
            <Button type="button" size="sm" onClick={() => decide(true)}><Check /> {copy.apply}</Button>
            <Button type="button" size="sm" variant="ghost" onClick={() => decide(false)}>{copy.dismiss}</Button>
          </>
        ) : (
          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
            {state === "dismissed" ? <X className="size-3.5" aria-hidden="true" /> : <Check className="size-3.5" aria-hidden="true" />}
            {state === "dismissed" ? copy.dismissed : copy.applied}
          </span>
        )}
      </div>
    </div>
  );
}
