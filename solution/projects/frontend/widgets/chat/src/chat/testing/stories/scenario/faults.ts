import type { Beat, Scenario } from "./model";

/**
 * What can go wrong on the way, each one a thing a real transport does.
 *
 * Event faults rewrite the beats, so both transports see the same fault. `abort` and `reconnect` act on the
 * host (Stop pressed; the thread reloaded from the server), so they are read by the player harness, not here.
 */
export const FAULTS = ["none", "duplicate", "out-of-order", "drop-terminal", "tool-timeout", "offline", "abort", "reconnect"] as const;
export type Fault = (typeof FAULTS)[number];

export const FAULT_NOTE: Readonly<Record<Fault, string>> = {
  none: "The run as the server sent it.",
  duplicate: "The first step frame arrives twice. The row is updated in place, never added again.",
  "out-of-order": "The first step settles before it starts. The older frame is refused; the row is not reopened.",
  "drop-terminal": "The stream ends with no final frame. The turn reads as interrupted, not as failed.",
  "tool-timeout": "The first tool call times out. The row shows the timeout and keeps the server's words.",
  offline: "Nothing reaches a server. The turn fails once, with one plain sentence.",
  abort: "Stop is pressed halfway. Open calls close as stopped, never as failed.",
  reconnect: "The stream is cut, then the stored answer is loaded from the server and replaces the partial one.",
};

const isStep = (beat: Beat): beat is Extract<Beat, { kind: "step" }> => beat.kind === "step";

/** The beats the transport sees under this fault. */
export function applyFault(beats: readonly Beat[], fault: Fault): readonly Beat[] {
  switch (fault) {
    case "duplicate": {
      const out: Beat[] = [];
      let done = false;
      for (const beat of beats) {
        out.push(beat);
        if (beat.kind === "step" && !done) {
          done = true;
          out.push({ ...beat, at: beat.at + 1 });
        }
      }
      return out;
    }
    case "out-of-order": {
      const first = beats.find(isStep);
      if (first === undefined) return beats;
      const id = first.step.step_id;
      const pair = beats.filter((beat) => isStep(beat) && beat.step.step_id === id);
      const [running, settled] = pair;
      if (running === undefined || settled === undefined || !isStep(running) || !isStep(settled)) return beats;
      // The settled frame is delivered where the running one was, and the running one where the settled one was.
      return beats.map((beat) => (beat === running ? { ...settled, at: running.at } : beat === settled ? { ...running, at: settled.at } : beat));
    }
    case "drop-terminal":
    case "reconnect": {
      const kept = beats.filter((beat) => beat.kind !== "finish" && beat.kind !== "fail" && beat.kind !== "lost");
      return kept;
    }
    case "tool-timeout": {
      const first = beats.find((beat) => isStep(beat) && beat.step.kind === "tool" && beat.step.status !== "running");
      if (first === undefined || !isStep(first)) return beats;
      return beats.map((beat) =>
        beat === first
          ? { ...first, step: { ...first.step, status: "timeout", duration_ms: 30_000, summary: "The service did not answer in time", error: { code: "timeout", retryable: true } } }
          : beat,
      );
    }
    case "offline":
      return [{ kind: "offline", at: 400 }];
    case "none":
    case "abort":
      return beats;
  }
}

/** The scenario as the transport will see it under a fault. */
export function withFault(scenario: Scenario, fault: Fault): Scenario {
  const beats = applyFault(scenario.beats, fault);
  return beats === scenario.beats ? scenario : { ...scenario, beats };
}
