/**
 * Collapse runs of same-kind parts into groups.
 *
 * A turn that thinks, calls four tools, thinks again and answers renders as six
 * separate cards without this — the answer ends up below a wall of tool calls.
 * Grouping puts the run behind one "Thinking" or "4 tools" affordance, which is
 * what assistant-ui does and what makes a tool-heavy transcript readable.
 *
 * Only ADJACENT parts coalesce. Reordering to gather all tool calls together
 * would misrepresent the turn: the sequence is the agent's reasoning, and
 * "searched, then read what it found" is different information from "searched
 * and read".
 */

import type { MessagePart, ToolPart } from "./parts";

export type PartGroup =
  /** A single part, rendered on its own. */
  | { readonly kind: "single"; readonly key: string; readonly part: MessagePart }
  /** Two or more adjacent parts of one type. */
  | {
      readonly kind: "run";
      readonly key: string;
      readonly type: MessagePart["type"];
      readonly parts: readonly MessagePart[];
    };

/** Types worth collapsing. Text is never grouped — prose is the answer itself. */
const GROUPABLE = new Set<MessagePart["type"]>(["reasoning", "tool"]);

export function groupParts(parts: readonly MessagePart[]): readonly PartGroup[] {
  const groups: PartGroup[] = [];
  let run: MessagePart[] = [];

  const flush = (): void => {
    const first = run[0];
    if (first === undefined) return;
    groups.push(
      run.length === 1
        ? { kind: "single", key: first.id, part: first }
        // Keyed on the FIRST member: a run that grows while streaming keeps its
        // key, so the group does not remount on every new tool call.
        : { kind: "run", key: first.id, type: first.type, parts: run },
    );
    run = [];
  };

  for (const part of parts) {
    const previous = run[0];
    const continues =
      previous !== undefined && previous.type === part.type && GROUPABLE.has(part.type);
    if (!continues) flush();
    if (GROUPABLE.has(part.type)) {
      run.push(part);
      continue;
    }
    groups.push({ kind: "single", key: part.id, part });
  }
  flush();

  return groups;
}

/**
 * Should a group be open?
 *
 * Open while the run is still producing, collapsed once it settles — the user
 * wants to watch a tool work and then get it out of the way. Derived rather
 * than stored so it cannot disagree with the parts; a host that wants manual
 * control layers its own state over this default.
 */
export function isGroupActive(group: PartGroup): boolean {
  const parts = group.kind === "run" ? group.parts : [group.part];
  return parts.some(
    (part) =>
      part.type === "tool" &&
      (part.toolState.state === "input-streaming" ||
        part.toolState.state === "input-available"),
  );
}

/** What to draw for a group: a part on its own, or several settled calls behind one counter. */
export type FoldItem =
  | { readonly kind: "part"; readonly part: MessagePart }
  | { readonly kind: "fold"; readonly key: string; readonly parts: readonly ToolPart[] };

/** A call that finished and has nothing to say: it may disappear into the counter. */
function foldsAway(part: MessagePart): part is ToolPart {
  return (
    part.type === "tool" &&
    part.toolState.state === "output-available" &&
    (part.meta?.status === undefined || part.meta.status === "ok")
  );
}

/**
 * The fold policy for a run of tool calls (the retired `ui-chat`'s, kept whole):
 *
 * 1. Nothing folds while any call is still running; the reader is watching.
 * 2. Once idle, calls that succeeded fold into ONE counter ("3 tools used").
 * 3. A call that failed, timed out or was stopped stays visible and never folds:
 *    it is why the turn went the way it did.
 *
 * Two or more successes fold; a lone one is drawn as itself, because "1 tool
 * used" would hide a card behind a click to say what the card already says. The
 * counter comes first and the visible calls keep their arrival order after it.
 * Reasoning and single parts are never folded.
 */
export function planFold(group: PartGroup): readonly FoldItem[] {
  if (group.kind === "single") return [{ kind: "part", part: group.part }];
  const each = group.parts.map((part): FoldItem => ({ kind: "part", part }));
  if (group.type !== "tool" || isGroupActive(group)) return each;
  const folded = group.parts.filter(foldsAway);
  const first = folded[0];
  if (first === undefined || folded.length < 2) return each;
  const shown = group.parts.filter((part) => !foldsAway(part));
  return [
    { kind: "fold", key: `fold:${first.id}`, parts: folded },
    ...shown.map((part): FoldItem => ({ kind: "part", part })),
  ];
}
