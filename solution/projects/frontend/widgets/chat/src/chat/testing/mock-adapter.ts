/**
 * A scripted adapter for stories and tests.
 *
 * Shipped from `src/` rather than kept in a test file because stories need it
 * too, and a second copy in the Storybook app would drift from the chunk
 * vocabulary it mimics. It is the reference implementation of `ChatAdapter`:
 * about forty lines, which is the argument that the one-method contract works.
 */

import type { ChatAdapter, SendRequest } from "../core/conversation/adapter";
import type { StreamChunk } from "../core/conversation/chunks";

export interface MockOptions {
  /** Chunks to replay per turn. A function receives the request. */
  readonly script: readonly StreamChunk[] | ((request: SendRequest) => readonly StreamChunk[]);
  /** Milliseconds between chunks. 0 replays synchronously. */
  readonly delayMs?: number;
}

export function mockAdapter(options: MockOptions): ChatAdapter {
  const { script, delayMs = 0 } = options;

  return {
    sendMessage(request) {
      const chunks = typeof script === "function" ? script(request) : script;
      let index = 0;

      return Promise.resolve(
        new ReadableStream<StreamChunk>({
          async pull(controller) {
            if (index >= chunks.length) {
              controller.close();
              return;
            }
            // Honour the signal between chunks so Stop works in a story the
            // same way it works against a real transport.
            if (request.signal.aborted) {
              controller.close();
              return;
            }
            if (delayMs > 0) await sleep(delayMs, request.signal);
            const chunk = chunks[index];
            index += 1;
            if (chunk !== undefined) controller.enqueue(chunk);
          },
        }),
      );
    },
  };
}

function sleep(ms: number, signal: AbortSignal): Promise<void> {
  return new Promise((resolve) => {
    const timer = setTimeout(resolve, ms);
    signal.addEventListener("abort", () => {
      clearTimeout(timer);
      resolve();
    }, { once: true });
  });
}

/** Split text into token-sized deltas — what makes a story look like streaming. */
export function tokenize(text: string, partId = "t1"): StreamChunk[] {
  const words = text.split(/(\s+)/).filter((w) => w !== "");
  return [
    { type: "text-start", partId },
    ...words.map((delta): StreamChunk => ({ type: "text-delta", partId, delta })),
  ];
}
