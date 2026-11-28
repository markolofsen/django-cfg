import { describe, expect, it } from "vitest";

import type { StreamChunk } from "../../../core/conversation/chunks";
import { toChunks, toFrames } from "./compile";
import { FAULTS, withFault, type Fault } from "./faults";
import { adapterChunks, chunksOf, COPY, messageOf } from "./harness";
import { TURNS as SCENARIOS } from "../library";

/** `createdAt` is the one field the adapter stamps with the clock; the fixture pins it. */
const bare = (chunks: readonly StreamChunk[]): StreamChunk[] => chunks.map((chunk) => (chunk.type === "message-start" ? { ...chunk, createdAt: 0 } : chunk));

const EVENT_FAULTS: readonly Fault[] = ["none", "duplicate", "out-of-order", "drop-terminal", "tool-timeout", "offline"];

describe("one scenario, two transports", () => {
  for (const fault of EVENT_FAULTS) {
    describe(`fault: ${fault}`, () => {
      for (const clean of SCENARIOS) {
        it(`${clean.id}: the chunk path and the frame path build the same transcript`, async () => {
          const scenario = withFault(clean, fault);
          const direct = chunksOf(scenario);
          const viaFrames = await adapterChunks(scenario);
          // A stream with no final frame is closed by the adapter with `interrupted`; the store does the same for the chunk path.
          const expected = scenario.beats.every((beat) => beat.kind !== "finish" && beat.kind !== "fail" && beat.kind !== "lost" && beat.kind !== "offline") ? [...direct, { type: "interrupted" } as StreamChunk] : direct;
          expect(bare(viaFrames)).toEqual(bare(expected));
          expect(messageOf(viaFrames).parts).toEqual(messageOf(expected).parts);
        });
      }
    });
  }

  it("the failure sentence of an offline turn is the catalogue's", async () => {
    const offline = withFault(SCENARIOS[0]!, "offline");
    const message = messageOf(await adapterChunks(offline));
    expect(message.status).toEqual({ state: "failed", message: COPY.failed });
  });

  it("every scenario compiles to timed items in order", () => {
    for (const scenario of SCENARIOS) {
      for (const items of [toChunks(scenario, COPY), toFrames(scenario)]) {
        const times = items.map(({ at }) => at);
        expect(times, scenario.id).toEqual([...times].sort((a, b) => a - b));
      }
    }
  });

  it("covers every fault the injector offers", () => {
    expect([...EVENT_FAULTS, "abort", "reconnect"].sort()).toEqual([...FAULTS].sort());
  });
});
