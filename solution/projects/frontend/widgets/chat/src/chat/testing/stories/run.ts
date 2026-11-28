import type { ChatAdapter } from "../../core/conversation/adapter";
import type { StreamChunk } from "../../core/conversation/chunks";
import { createStreamAdapter } from "../../../assistant/session";
import type { ChatTransport } from "../../../assistant/wire";
import { CLIENT_ID, toChunks, toFrames, withFault, TimelinePlayer, type Fault, type FrameItem, type Scenario, type Timed } from "./scenario";

/** Which path the scenario takes to the transcript: straight chunks, or frames through the assistant's own adapter. */
export type Transport = "chunks" | "frames";

/** The player of the turn in flight. A turn creates it when it starts, so controls follow whatever is running. */
export interface PlayerSlot {
  get(): TimelinePlayer<unknown> | null;
  subscribe(listener: () => void): () => void;
  set(player: TimelinePlayer<unknown> | null): void;
}

export function createSlot(): PlayerSlot {
  let current: TimelinePlayer<unknown> | null = null;
  const listeners = new Set<() => void>();
  return {
    get: () => current,
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    set(player) {
      current = player;
      for (const listener of listeners) listener();
    },
  };
}

export interface RunOptions {
  readonly transport: Transport;
  readonly fault: Fault;
  readonly speed: number;
  readonly autoplay: boolean;
  /** The one sentence a failed turn says, in the reader's language. */
  readonly failed: string;
  readonly slot: PlayerSlot;
  readonly onInterrupted?: () => void;
}

const asPlayer = <T,>(player: TimelinePlayer<T>): TimelinePlayer<unknown> => player as unknown as TimelinePlayer<unknown>;

function chunkAdapter(items: readonly Timed<StreamChunk>[], options: RunOptions): ChatAdapter {
  return {
    sendMessage: ({ signal }) =>
      Promise.resolve(
        new ReadableStream<StreamChunk>({
          start(controller) {
            const player = new TimelinePlayer(items, { speed: options.speed, autoplay: options.autoplay });
            options.slot.set(asPlayer(player));
            const close = () => {
              try {
                controller.close();
              } catch {
                // closed already by Stop
              }
            };
            player.attach((chunk) => controller.enqueue(chunk), close);
            signal.addEventListener("abort", () => {
              player.detach();
              close();
            }, { once: true });
          },
        }),
      ),
  };
}

function frameTransport(items: readonly Timed<FrameItem>[], options: RunOptions): ChatTransport {
  return {
    async *open({ signal }) {
      const player = new TimelinePlayer(items, { speed: options.speed, autoplay: options.autoplay });
      options.slot.set(asPlayer(player));
      const queue: FrameItem[] = [];
      let finished = false;
      let wake: (() => void) | null = null;
      const poke = () => wake?.();
      player.attach((item) => {
        queue.push(item);
        poke();
      }, () => {
        finished = true;
        poke();
      });
      signal.addEventListener("abort", () => {
        player.detach();
        finished = true;
        poke();
      }, { once: true });
      for (;;) {
        const next = queue.shift();
        if (next !== undefined) {
          if ("throw" in next) throw next.throw;
          yield next.frame;
          continue;
        }
        if (finished) return;
        await new Promise<void>((resolve) => {
          wake = resolve;
        });
        wake = null;
      }
    },
  };
}

/** The adapter a chat sends its turn through: the scenario, under a fault, played by a player the controls can hold. */
export function scenarioAdapter(scenario: Scenario, options: RunOptions): ChatAdapter {
  const played = withFault(scenario, options.fault);
  if (options.transport === "chunks") return chunkAdapter(toChunks(played, { failed: options.failed }), options);
  return createStreamAdapter({
    transport: frameTransport(toFrames(played), options),
    getContext: () => undefined,
    onStatus: () => {},
    messages: { rejected: () => options.failed, streamError: (_code, message) => message, failed: options.failed },
    coalesceMs: 0,
    newId: () => CLIENT_ID,
    ...(options.onInterrupted === undefined ? {} : { onInterrupted: options.onInterrupted }),
  });
}
