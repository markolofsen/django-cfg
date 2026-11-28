import { ChevronDown, FileText, Undo2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@djangocfg/ui-core/components";

import { useChatCopy } from "../../i18n";
import type { ChangesPayload } from "./payload";
import { BLOCK_CARD } from "./style";

export interface ChangesBlockProps {
  readonly data: ChangesPayload;
  readonly onUndo?: () => void;
  readonly settled?: boolean;
}

/** A change that already happened: its title, "Show changes" opening a scrollable list of what it touched, and Undo when the payload allows it. */
export function ChangesBlock({ data, onUndo, settled = false }: ChangesBlockProps) {
  const copy = useChatCopy().blocks;
  const [shown, setShown] = useState(false);
  const [undone, setUndone] = useState(false);

  return (
    <div className={BLOCK_CARD} data-block="changes" data-undone={undone ? "true" : "false"}>
      <p className="font-medium">{data.title}</p>
      <div className="mt-2 flex items-center gap-2">
        {data.items.length > 0 ? (
          <Button type="button" size="sm" variant="secondary" aria-expanded={shown} onClick={() => setShown(!shown)}>
            {shown ? copy.hideChanges : copy.showChanges}
            <ChevronDown className={`size-3.5 transition-transform ${shown ? "rotate-180" : ""}`} aria-hidden="true" />
          </Button>
        ) : null}
        {data.undoable && onUndo ? (
          undone ? (
            <span className="text-xs text-muted-foreground">{copy.undone}</span>
          ) : (
            <Button type="button" size="sm" variant="ghost" disabled={settled} onClick={() => { setUndone(true); onUndo(); }}>
              <Undo2 /> {copy.undo}
            </Button>
          )
        ) : null}
      </div>
      {shown ? (
        <ul className="mt-2 max-h-56 divide-y overflow-y-auto rounded-lg border">
          {data.items.map((item, index) => (
            <li key={`${index}-${item.label}`} className="flex items-center gap-2 px-2.5 py-1.5">
              <FileText className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
              {item.href ? <a href={item.href} className="truncate underline-offset-2 hover:underline">{item.label}</a> : <span className="truncate">{item.label}</span>}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
