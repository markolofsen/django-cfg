import { useState } from "react";

import { Button, Input } from "@djangocfg/ui-core/components";

import { useChatCopy } from "../../i18n";
import type { AskPayload } from "./payload";
import { BLOCK_CARD } from "./style";

export interface AskBlockProps {
  readonly data: AskPayload;
  /** The answer, as the text the user picked or typed. */
  readonly onAnswer: (answer: string) => void;
  /** Already answered (here or earlier): shows the choice, offers nothing. */
  readonly settled?: boolean;
}

/** A question from the agent: option buttons, and a typed answer when `other` allows one. One answer, then it locks and shows what was chosen. */
export function AskBlock({ data, onAnswer, settled = false }: AskBlockProps) {
  const copy = useChatCopy().blocks;
  const [chosen, setChosen] = useState<string | null>(null);
  const [typed, setTyped] = useState("");
  const locked = settled || chosen !== null;
  const answer = (value: string) => {
    if (locked) return;
    setChosen(value);
    onAnswer(value);
  };
  const free = data.other !== false;

  return (
    <div className={BLOCK_CARD} data-block="ask" data-locked={locked ? "true" : "false"}>
      {data.question ? <p className="font-medium">{data.question}</p> : null}
      {data.options.length > 0 ? (
        <div className="mt-2 flex flex-col gap-1.5" role="group" aria-label={data.question}>
          {data.options.map((option) => (
            <Button
              key={option.label}
              type="button"
              size="sm"
              variant={chosen === option.label ? "default" : "outline"}
              disabled={locked}
              onClick={() => answer(option.label)}
              className="h-auto justify-start whitespace-normal py-1.5 text-left"
            >
              <span className="flex flex-col items-start">
                <span>{option.label}</span>
                {option.description ? <span className="text-xs font-normal opacity-70">{option.description}</span> : null}
              </span>
            </Button>
          ))}
        </div>
      ) : null}
      {free && !locked ? (
        <form
          className="mt-2 flex gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            if (typed.trim() !== "") answer(typed.trim());
          }}
        >
          <Input value={typed} onChange={(event) => setTyped(event.target.value)} placeholder={typeof data.other === "string" ? data.other : copy.answerPlaceholder} aria-label={copy.answerPlaceholder} />
          <Button type="submit" size="sm" disabled={typed.trim() === ""}>{copy.sendAnswer}</Button>
        </form>
      ) : null}
      {locked ? <p className="mt-2 text-xs text-muted-foreground">{chosen ? `${copy.answered}: ${chosen}` : copy.answered}</p> : null}
    </div>
  );
}
