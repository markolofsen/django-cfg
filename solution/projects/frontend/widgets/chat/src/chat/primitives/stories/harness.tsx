import { useEffect } from "react";

import type { StreamChunk } from "../../core/conversation/chunks";
import type { ChatMessage } from "../../core/conversation/parts";
import type { PartRenderProps } from "../parts/part-registry";
import { ChatProvider, useChatStore } from "../../store";
import { mockAdapter } from "../../testing/mock-adapter";
import { Message } from "../parts/message";
import { PartRegistryProvider, type PartRegistry } from "../parts/part-registry";
import { Transcript } from "../transcript/transcript";
// From `ui/`, which primitives may not import — allowed here because the
// workbench never ships (`layers.test.ts` exempts it by name). Both are styled,
// and the tool renderer is the SHIPPED one, so a story cannot pass against a
// card the product does not draw.
import { PendingIndicator } from "../../ui/transcript/pending";
import { ToolRenderer } from "../../ui/renderers/tool";

/**
 * The workbench the transcript stories share.
 *
 * One set of renderers, not one per story file: a second copy would let a
 * story pass against renderers nothing ships, which is the failure mode a
 * workbench exists to prevent.
 *
 * Light and dark come from the preview's `withThemeByClassName` decorator and
 * its toolbar (`.storybook/preview.tsx`). Do NOT add a switcher or duplicate a
 * story per theme; semantic token classes make one story set correct in both.
 */

const bare = "grid gap-3 p-4 text-foreground";

function TextPart({ part }: PartRenderProps) {
  if (part.type !== "text") return null;
  return <p className="m-0 whitespace-pre-wrap">{part.text}</p>;
}

function ReasoningPart({ part }: PartRenderProps) {
  if (part.type !== "reasoning") return null;
  return (
    <details>
      <summary className="text-muted-foreground">Thinking</summary>
      <p className="m-0 text-muted-foreground">{part.text}</p>
    </details>
  );
}

/**
 * Tool calls render through the SHIPPED renderer, not a copy.
 *
 * This workbench used to keep its own: a pulsing dot, no disclosure, no running
 * border. Every story passed while showing a screen the product no longer had —
 * the exact failure a workbench exists to prevent. `ui/` is reachable here
 * because `layers.test.ts` exempts this file by name, the same allowance
 * `PendingIndicator` already uses.
 *
 * The subagent thread comes with it: `PartRegistryProvider` is a context, so a
 * nested tool resolves through this same registry with nothing re-registered.
 */
const renderers: PartRegistry = {
  text: TextPart,
  reasoning: ReasoningPart,
  tool: ToolRenderer,
};

export interface HarnessProps {
  readonly script: readonly StreamChunk[];
  readonly delayMs?: number;
  readonly prompt?: string;
  /**
   * Seed the transcript instead of streaming it. `ToolPart.messages` has no
   * chunk in the wire vocabulary — an adapter that ran a subagent populates it
   * directly — so `store.load()` is the only honest way to reach that state.
   */
  readonly history?: readonly ChatMessage[];
}

/** Drives one turn on mount so a story shows a conversation, not an empty box. */
export function Harness({ script, delayMs = 40, prompt = "Show me the log", history }: HarnessProps) {
  return (
    <ChatProvider adapter={mockAdapter({ script, delayMs })}>
      <PartRegistryProvider renderers={renderers}>
        {history === undefined ? <AutoSend prompt={prompt} /> : <LoadHistory messages={history} />}
        <Transcript
          empty={<p className="text-muted-foreground">No messages yet.</p>}
          className="chat-transcript bg-background"
          pending={() => (
            <PendingIndicator
              className="text-muted-foreground flex items-center gap-2 py-3 text-sm"
              label="Thinking"
            />
          )}
        >
          {(id) => (
            <div className={bare}>
              <Message id={id} />
            </div>
          )}
        </Transcript>
      </PartRegistryProvider>
    </ChatProvider>
  );
}

function AutoSend({ prompt }: { readonly prompt: string }) {
  const store = useChatStore();
  useEffect(() => {
    void store.send({ text: prompt });
  }, [store, prompt]);
  return null;
}

function LoadHistory({ messages }: { readonly messages: readonly ChatMessage[] }) {
  const store = useChatStore();
  useEffect(() => {
    store.load(messages);
  }, [store, messages]);
  return null;
}
