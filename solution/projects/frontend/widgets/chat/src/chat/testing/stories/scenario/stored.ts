import type { StoredMessage, StoredThread } from "../../../../assistant/wire";
import type { Beat, Scenario } from "./model";

const settled = (beats: readonly Beat[]): unknown[] => {
  const last = new Map<string, unknown>();
  for (const beat of beats) if (beat.kind === "step") last.set(String(beat.step.step_id), beat.step);
  return [...last.values()];
};

/**
 * What the server would hold for a finished turn: the user's words, then the answer with its trace, its text and its cards.
 * The history endpoint's shape, so `fromStoredThread` (the shipped reader) turns it into the transcript a reload shows.
 */
export function storedTurn(scenario: Scenario, now = Date.UTC(2026, 10, 10, 9, 0, 0)): StoredMessage[] {
  const steps = settled(scenario.beats);
  const text = scenario.beats.flatMap((beat) => (beat.kind === "say" ? [beat.text] : [])).join("");
  const cards = scenario.beats.flatMap((beat) => (beat.kind === "payload" ? [{ kind: beat.name, data: beat.data }] : []));
  return [
    { id: `${scenario.messageId}-user`, seq: 1, role: "user", text: scenario.prompt, parts: [], status: "done", error_code: null, created_at: new Date(now).toISOString() },
    {
      id: scenario.messageId,
      seq: 2,
      role: "assistant",
      text,
      parts: cards,
      trace: steps.length === 0 ? null : { v: 1, status: "ok", steps_count: steps.length, steps },
      status: "done",
      error_code: null,
      created_at: new Date(now + 1000).toISOString(),
    },
  ];
};

export const storedThreadRow = (scenario: Scenario): StoredThread => ({ id: scenario.id, title: scenario.prompt, last_message_at: new Date(Date.UTC(2026, 10, 10, 9, 0, 0)).toISOString(), message_count: 2 });
