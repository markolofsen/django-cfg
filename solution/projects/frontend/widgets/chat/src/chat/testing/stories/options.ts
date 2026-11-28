import type { RunOptions as RunBlockOptions } from "../../ui/run";

/** What a reader sees of a step's detail. `public` is a visitor on a public chat; `admin` is a signed-in operator. */
export type Privacy = "default" | "public" | "admin";
export type ArgsMode = "hidden" | "keys" | "masked" | "full";
export type ResultMode = "hidden" | "preview" | "full";

export interface ViewArgs {
  readonly argsMode?: ArgsMode;
  readonly resultMode?: ResultMode;
  readonly labelsOnly: boolean;
  readonly showReasoningText: boolean;
  readonly defaultOpen: boolean;
  readonly runBlock: boolean;
}

export const PRIVACY_PRESETS: Readonly<Record<Privacy, Partial<ViewArgs>>> = {
  default: {},
  public: { labelsOnly: true, showReasoningText: false },
  admin: { argsMode: "full", resultMode: "full", showReasoningText: true, labelsOnly: false },
};

export const DEFAULT_VIEW: ViewArgs = { labelsOnly: false, showReasoningText: false, defaultOpen: false, runBlock: true };

/** The options the shipped `createRunRenderer` takes, from what the story's args say. */
export function runOptionsOf(view: ViewArgs): RunBlockOptions {
  return {
    defaultOpen: view.defaultOpen,
    labelsOnly: view.labelsOnly,
    showReasoningText: view.showReasoningText,
    ...(view.argsMode === undefined ? {} : { argsMode: view.argsMode }),
    ...(view.resultMode === undefined ? {} : { resultMode: view.resultMode }),
  };
}
