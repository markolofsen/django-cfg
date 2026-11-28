import type { Scenario, ScenarioGroup } from "../scenario";
import { approval, pageCopilot, question, sources } from "./blocks";
import { errorAfterPartial, interrupted, offline } from "./failures";
import { longContent, plainAnswer } from "./messages";
import { attachments, restoredSession } from "./history";
import { privacy } from "./privacy";
import { hiddenThought, longResultScenario, longRunScenario, parallelBatch, reasoning, retryChain, toolCancelled, toolError, toolRun, toolTimeout } from "./tools";

/** Every scenario, in the order the overview lists its group. Ids are unique; `library.test.ts` holds the line. */
export const SCENARIOS: readonly Scenario[] = [
  plainAnswer,
  longContent,
  reasoning,
  hiddenThought,
  toolRun,
  toolError,
  toolTimeout,
  toolCancelled,
  parallelBatch,
  retryChain,
  longRunScenario,
  longResultScenario,
  question,
  approval,
  sources,
  pageCopilot,
  errorAfterPartial,
  interrupted,
  offline,
  restoredSession,
  attachments,
  privacy,
];

/** The scenarios that play a turn (the others only restore a thread). */
export const TURNS: readonly Scenario[] = SCENARIOS.filter((scenario) => scenario.beats.length > 0);

export const scenarioById = (id: string): Scenario => {
  const found = SCENARIOS.find((candidate) => candidate.id === id);
  if (found === undefined) throw new Error(`no scenario "${id}"`);
  return found;
};

export const inGroup = (group: ScenarioGroup): readonly Scenario[] => SCENARIOS.filter((scenario) => scenario.group === group);

export * from "./payloads";
export { SESSION_ROWS } from "./history";
