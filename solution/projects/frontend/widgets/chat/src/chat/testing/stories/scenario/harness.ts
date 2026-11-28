import type { SendRequest } from "../../../core/conversation/adapter";
import type { StreamChunk } from "../../../core/conversation/chunks";
import type { ChatMessage } from "../../../core/conversation/parts";
import { emptyTranscript, reduceAll, selectMessages } from "../../../core/conversation/transcript";
import { createStreamAdapter } from "../../../../assistant/session";
import type { ChatTransport } from "../../../../assistant/wire";
import { CLIENT_ID, toChunks, toFrames, type FrameItem, type Timed } from "./compile";
import type { Scenario } from "./model";

export const COPY = { failed: "Something went wrong. Try again." } as const;

/** A transport that hands its items over at once. Used where the clock does not matter. */
export const instantTransport = (items: readonly Timed<FrameItem>[]): ChatTransport => ({
  async *open() {
    for (const { item } of items) {
      if ("throw" in item) throw item.throw;
      yield item.frame;
    }
  },
});

export const request = (text: string): SendRequest => ({ text, history: [], recipient: "all", mentions: [], messageId: "user-1", attachments: [], signal: new AbortController().signal });

/** The production adapter, fed the scenario's frames: what the assistant's wire does with them. */
export function adapterChunks(scenario: Scenario, items: readonly Timed<FrameItem>[] = toFrames(scenario)): Promise<StreamChunk[]> {
  const adapter = createStreamAdapter({
    transport: instantTransport(items),
    getContext: () => undefined,
    onStatus: () => {},
    messages: { rejected: () => COPY.failed, streamError: (_code, message) => message, failed: COPY.failed },
    coalesceMs: 0,
    newId: () => CLIENT_ID,
  });
  return adapter.sendMessage(request(scenario.prompt)).then(async (stream) => {
    const out: StreamChunk[] = [];
    const reader = stream.getReader();
    for (;;) {
      const { done, value } = await reader.read();
      if (done) return out;
      out.push(value);
    }
  });
}

/** The first assistant message a chunk stream builds. */
export function messageOf(chunks: readonly StreamChunk[]): ChatMessage {
  const message = selectMessages(reduceAll(emptyTranscript, chunks))[0];
  if (message === undefined) throw new Error("no message produced");
  return message;
}

export const chunksOf = (scenario: Scenario): StreamChunk[] => toChunks(scenario, COPY).map(({ item }) => item);
