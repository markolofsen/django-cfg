import { Check, Copy } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { useChatCopy } from "../../../i18n";

/** Copies the trace as Markdown: exactly what the screen shows. Drawn only inside the opened block, at the end of the list. */
export function CopyTrace({ markdown }: { markdown: () => string }) {
  const { run } = useChatCopy();
  const [copied, setCopied] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => void (timer.current && clearTimeout(timer.current)), []);

  const copy = async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(markdown());
      setCopied(true);
      timer.current = setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard refused: the button simply does not confirm */
    }
  };
  return (
    <>
      <button type="button" className="chat-run-copy" aria-label={run.copy} title={run.copy} onClick={() => void copy()}>
        {copied ? <Check aria-hidden /> : <Copy aria-hidden />}
      </button>
      <span className="sr-only" role="status">
        {copied ? run.copied : ""}
      </span>
    </>
  );
}
