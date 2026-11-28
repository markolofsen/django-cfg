import { ChevronDown } from "lucide-react";
import { memo, useId, useMemo, useState, type KeyboardEvent } from "react";

import { isRovingKey, nextIndex } from "../../core/screen/roving";
import { runToMarkdown, type ExportWords } from "../../core/run/export";
import { PAGE_SIZE, windowSteps } from "../../core/run/paging";
import { phraseText, stepPhrase, type PhraseWords, type StepPhrase } from "../../core/run/phrase";
import { detailOf, resolvePrivacy, type ResolvedPrivacy } from "../../core/run/privacy";
import { selectRun, stepTitle, type RunStep } from "../../core/run/view";
import type { RunPart } from "../../core/conversation/parts";
import { fill, useChatCopy, useChatLanguage } from "../../../i18n";
import { CopyTrace } from "./actions";
import type { RunOptions } from "./options";
import { StepRow } from "./step";
import { runSummary } from "./summary";

export interface RunBlockProps {
  readonly run: RunPart;
  readonly options?: RunOptions;
  /** Resolved once by the renderer factory; resolved here when a host mounts the block itself. */
  readonly privacy?: ResolvedPrivacy;
}

/**
 * What the answer did, as one quiet line ("Worked for 10s") that opens into a flat
 * list of one-line steps under a thin rule.
 *
 * Collapsed while it works and once it settled (the answer is what the reader came
 * for); it opens itself when a step failed or was stopped. The reader's own click wins
 * over both, and nothing closes a failed step. Everything shown comes from `selectRun`,
 * the headless view of the parts, and from the privacy in force.
 */
export const RunBlock = memo(function RunBlock({ run: part, options = {}, privacy: given }: RunBlockProps) {
  const copy = useChatCopy();
  const language = useChatLanguage();
  const id = useId();
  const privacy = useMemo(() => given ?? resolvePrivacy(options), [given, options]);
  const view = useMemo(() => selectRun(part.parts), [part.parts]);
  const [override, setOverride] = useState<boolean | null>(options.defaultOpen ?? null);
  const [limit, setLimit] = useState(PAGE_SIZE);

  const kindWord = (kind: string): string => (Object.hasOwn(copy.run.kind, kind) ? copy.run.kind[kind as keyof typeof copy.run.kind] : copy.run.kind.note);
  const words: PhraseWords = { verb: copy.run.verb, kind: kindWord };
  /** A server-named object (a source's title) only where the privacy lets sources out at all. */
  const phrase = (step: RunStep): StepPhrase => stepPhrase(step, words, options.labels, detailOf(step, privacy).sources?.[0]?.title);
  const title = (step: RunStep): string => stepTitle(step, options.labels, kindWord);
  const open = override ?? (view.counts.failed > 0 || view.counts.cancelled > 0);
  const summary = runSummary(view, copy, language, (step) => phraseText(phrase(step)));
  const win = open ? windowSteps(view.steps, limit, title) : null;
  const exportWords: ExportWords = { title, status: (s) => copy.run.status[s as keyof typeof copy.run.status] ?? s, arguments: copy.run.arguments, result: copy.run.result };

  if (view.steps.length === 0) return null;

  const onKeyDown = (event: KeyboardEvent<HTMLOListElement>): void => {
    if (!isRovingKey(event.key)) return;
    const toggles = [...event.currentTarget.querySelectorAll<HTMLElement>("[data-run-toggle]")];
    const next = nextIndex(event.key, toggles.indexOf(document.activeElement as HTMLElement), toggles.length);
    if (next === null || toggles.indexOf(document.activeElement as HTMLElement) < 0) return;
    event.preventDefault();
    toggles[next]?.focus();
  };

  return (
    <section className="chat-run" data-status={view.status}>
      <div className="chat-run-head">
        <button type="button" className="chat-run-toggle" aria-expanded={open} aria-controls={id} aria-label={`${summary.text}. ${open ? copy.run.hide : copy.run.show}`} onClick={() => setOverride(!open)}>
          <span className="chat-run-line" data-tone={summary.tone}>
            {summary.text}
          </span>
          <ChevronDown className="chat-run-chevron" aria-hidden />
        </button>
      </div>
      {/* Announced once, when the run settles: a per-step announcement while it works would talk over the answer. */}
      <span className="sr-only" role="status">
        {view.status === "running" ? "" : summary.text}
      </span>
      {open && win !== null ? (
        <div id={id} className="chat-run-body">
          <ol className="chat-run-steps" aria-label={copy.run.label} onKeyDown={onKeyDown}>
            {win.earlier === null ? null : (
              <li className="chat-run-earlier">
                {fill(copy.run.earlier, { count: win.earlier.count })}: {win.earlier.top.map((t) => `${t.name} ×${t.count}`).join(", ")}
              </li>
            )}
            {win.shown.map((step) => (
              <StepRow key={step.id} step={step} phrase={phrase(step)} privacy={privacy} />
            ))}
          </ol>
          {win.hidden > 0 ? (
            <button type="button" className="chat-run-more" onClick={() => setLimit(limit + PAGE_SIZE)}>
              {fill(copy.run.more, { count: Math.min(PAGE_SIZE, win.hidden) })}
            </button>
          ) : null}
          {view.omitted === undefined ? null : <p className="chat-run-note">{fill(copy.run.omitted, { count: view.omitted })}</p>}
          {options.allowCopy === false ? null : <CopyTrace markdown={() => runToMarkdown(view, privacy, exportWords)} />}
        </div>
      ) : null}
    </section>
  );
});
