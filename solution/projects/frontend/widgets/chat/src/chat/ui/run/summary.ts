import type { Locale } from "@djangocfg/i18n/copy";
import { formatDurationMs } from "@djangocfg/widget-kit";

import { fill, plural, type ChatCopy } from "../../../i18n";
import type { RunStep, RunView } from "../../core/run/view";

export type SummaryTone = "live" | "ok" | "warn" | "muted";

/** "10s" for a header: whole seconds (at least 1), never a decimal; a minute or more reads as the kit's "1m 5s". */
const spoken = (ms: number): string => (ms < 60_000 ? `${Math.max(1, Math.round(ms / 1000))}s` : formatDurationMs(ms));

/**
 * The one quiet line a run reads as: "Reading 3 emails… · 2 tools" while it works,
 * "Worked for 10s" once it settled, "Worked for 10s · 1 failed" when a call failed,
 * "Stopped · 3 tools" when the turn ended before it finished.
 * `title` is a step's live phrase (the server's words, the host's map or a template).
 */
export function runSummary(view: RunView, copy: ChatCopy, language: Locale, title: (step: RunStep) => string): { text: string; tone: SummaryTone } {
  const { run, tool } = copy;
  const { counts } = view;
  const join = (...parts: (string | undefined)[]): string => parts.filter((p): p is string => p !== undefined && p !== "").join(" · ");
  const tools = counts.tools > 0 ? plural(run.tools, counts.tools, language) : undefined;

  if (view.status === "running") {
    const { current } = view;
    const live = current === undefined ? run.working : `${title(current).replace(/[.…]+$/, "")}…`;
    return { text: join(live, tools), tone: "live" };
  }
  if (view.status === "cancelled") return { text: join(tool.cancelled, tools), tone: "muted" };
  const worked = view.totalMs === undefined ? run.done : fill(run.worked, { time: spoken(view.totalMs) });
  if (view.status === "error") return { text: join(worked, fill(run.failed, { count: counts.failed })), tone: "warn" };
  return { text: worked, tone: "ok" };
}
