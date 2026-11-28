import type { ProposedAction } from "./proposal";

/**
 * The wire block an agent emits to propose a page action.
 *
 * A `data` part with `kind: 'ui-action'`, so it travels the transcript the
 * chat already has and needs no new channel. `readUiAction` takes `unknown`
 * and returns null on anything malformed — the renderer never guards a shape
 * twice.
 */
export interface UiActionBlock {
  /** Stable across re-renders and re-sends: the id every outcome is keyed on. */
  readonly id: string;
  readonly action: ProposedAction;
  /** What the button says it will do, in the agent's words. */
  readonly label: string;
}

/** `kind` of the data part this module reads. */
export const UI_ACTION_KIND = "ui-action";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function readAction(value: unknown): ProposedAction | null {
  if (!isRecord(value)) return null;
  const { kind, ref } = value;
  if (typeof ref !== "string" || ref.length === 0) return null;
  if (kind === "click") return { kind, ref };
  // A `fill` without a value is not a fill with an empty one: the agent
  // omitting it means it never decided what to type, and clearing the field
  // is a different action than the user is being asked to approve.
  if (kind === "fill" && typeof value.value === "string") {
    return { kind, ref, value: value.value };
  }
  return null;
}

export function readUiAction(data: unknown): UiActionBlock | null {
  if (!isRecord(data)) return null;
  const { id, label } = data;
  if (typeof id !== "string" || id.length === 0) return null;
  if (typeof label !== "string" || label.length === 0) return null;
  const action = readAction(data.action);
  if (action === null) return null;
  return { id, action, label };
}
