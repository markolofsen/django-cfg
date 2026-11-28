/**
 * The run as text a person can paste into a ticket: Markdown.
 *
 * Built from the same `StepDetail` the disclosure shows, so an export can never
 * carry more than the screen did.
 */

import { detailOf, type ResolvedPrivacy, type StepDetail } from "./privacy";
import type { RunStep, RunView } from "./view";

export interface ExportWords {
  /** A step's title (the host's label, the server's, or the generic word for its kind). */
  readonly title: (step: RunStep) => string;
  /** A status as a word. */
  readonly status: (status: string) => string;
  readonly arguments: string;
  readonly result: string;
}

const seconds = (ms: number): string => `${(ms / 1000).toFixed(ms < 10_000 ? 1 : 0)} s`;

function detailLines(detail: StepDetail, words: ExportWords): string[] {
  const lines: string[] = [];
  if (detail.purpose !== undefined) lines.push(`  - ${detail.purpose}`);
  if (detail.query !== undefined) lines.push(`  - ${detail.query}`);
  if (detail.args !== undefined) lines.push(`  - ${words.arguments}: ${detail.args.map((a) => (a.value === undefined ? a.key : `${a.key}=${a.value}`)).join(", ")}`);
  if (detail.result !== undefined) lines.push(`  - ${words.result}: ${detail.result.replace(/\s+/g, " ")}`);
  if (detail.sources !== undefined) lines.push(`  - ${detail.sources.map((s) => s.title ?? s.id).join("; ")}`);
  return lines;
}

export function runToMarkdown(view: RunView, privacy: ResolvedPrivacy, words: ExportWords): string {
  const rows = view.steps.flatMap((step, index) => {
    const dur = step.meta.durationMs === undefined ? "" : `, ${seconds(step.meta.durationMs)}`;
    const summary = step.meta.summary === undefined || step.meta.summary === "" ? "" : ` - ${step.meta.summary}`;
    return [`${index + 1}. ${words.title(step)} (${words.status(step.status)}${dur})${summary}`, ...detailLines(detailOf(step, privacy), words)];
  });
  return rows.join("\n");
}
