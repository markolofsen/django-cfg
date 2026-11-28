import { fill, useChatCopy } from "../../../i18n";
import type { StepDetail } from "../../core/run/privacy";

/** The second disclosure of a step: what the server let out, in the order a reader asks. Nothing here is computed from the raw input or output. */
export function StepDetailView({ detail, duration }: { detail: StepDetail; duration?: string }) {
  const { run } = useChatCopy();
  const { tokens } = detail;
  const rows: [string, React.ReactNode][] = [];
  if (detail.purpose !== undefined) rows.push([run.purpose, detail.purpose]);
  if (detail.query !== undefined) rows.push([run.query, detail.query]);
  if (detail.args !== undefined) {
    rows.push([
      run.arguments,
      <ul key="args" className="chat-run-list">
        {detail.args.map((a) => (
          <li key={a.key}>
            <code>{a.key}</code>
            {a.value === undefined ? null : <>: {a.value}</>}
          </li>
        ))}
      </ul>,
    ]);
  }
  if (detail.result !== undefined) rows.push([run.result, <pre key="result" className="chat-run-pre">{detail.result}{detail.resultClipped ? "…" : ""}</pre>]);
  if (detail.sources !== undefined) {
    rows.push([
      run.sources,
      <ul key="sources" className="chat-run-list">
        {detail.sources.map((s) => (
          <li key={`${s.kind}:${s.id}`}>{s.title ?? s.id}</li>
        ))}
      </ul>,
    ]);
  }
  const usage = [
    duration,
    detail.model,
    tokens?.input !== undefined || tokens?.output !== undefined ? fill(run.tokens, { input: tokens.input ?? 0, output: tokens.output ?? 0 }) : undefined,
    detail.costUsd === undefined ? undefined : `$${detail.costUsd.toFixed(4)}`,
    detail.errorCode,
  ].filter((x): x is string => x !== undefined);
  const notes = [detail.notShared ? run.notShared : undefined, detail.masked ? run.masked : undefined, detail.truncated ? run.truncated : undefined, detail.retryable === true ? run.retryable : undefined].filter((x): x is string => x !== undefined);
  if (rows.length === 0 && usage.length === 0 && notes.length === 0) return null;
  return (
    <div className="chat-run-detail">
      <dl>
        {rows.map(([term, value]) => (
          <div key={term} className="chat-run-row">
            <dt>{term}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      {usage.length > 0 ? <p className="chat-run-note">{usage.join(" · ")}</p> : null}
      {notes.length > 0 ? <p className="chat-run-note">{notes.join(" · ")}</p> : null}
    </div>
  );
}
