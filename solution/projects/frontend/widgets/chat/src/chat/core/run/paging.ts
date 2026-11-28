/**
 * How many steps of a long run are drawn.
 *
 * A step that failed or is still going is never hidden by paging. The rest are
 * shown a page at a time; past {@link STEP_CAP} the oldest settled steps fold into
 * one line that counts them by name, because a run that long is read as a total.
 */

import { isPinnedStep, type RunStep } from "./view";

export const PAGE_SIZE = 25;
export const STEP_CAP = 200;

export interface StepWindow {
  /** The steps drawn, in arrival order. */
  readonly shown: readonly RunStep[];
  /** Settled steps past the cap, folded into a summary line, with their most common names. */
  readonly earlier: { readonly count: number; readonly top: readonly { readonly name: string; readonly count: number }[] } | null;
  /** Steps still behind "Show more". */
  readonly hidden: number;
}

export function windowSteps(steps: readonly RunStep[], limit: number, title: (step: RunStep) => string): StepWindow {
  const foldedFrom = Math.max(0, steps.length - STEP_CAP);
  const folded = steps.slice(0, foldedFrom).filter((s) => !isPinnedStep(s));
  const foldedIds = new Set(folded.map((s) => s.id));
  const recent = steps.filter((s) => !foldedIds.has(s.id));
  let used = 0;
  const shown = recent.filter((step) => {
    if (isPinnedStep(step)) return true;
    used += 1;
    return used <= limit;
  });
  const counts = new Map<string, number>();
  for (const step of folded) counts.set(title(step), (counts.get(title(step)) ?? 0) + 1);
  const top = [...counts].sort((a, b) => b[1] - a[1]).slice(0, 3).map(([name, count]) => ({ name, count }));
  return { shown, earlier: folded.length === 0 ? null : { count: folded.length, top }, hidden: recent.length - shown.length };
}
