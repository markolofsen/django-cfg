/**
 * Hide an UNCLOSED `$$` from the math parser.
 *
 * ## The defect, measured
 *
 * streamdown completes half-arrived markdown so a bold run styles itself while
 * the model is still typing it. Applied to math that behaviour is wrong rather
 * than merely early: `complexity is $$O(n \log` renders a typeset `O(n log` —
 * a DIFFERENT expression from the one being written, which then jumps to
 * another as tokens land. A reader cannot tell an intermediate formula from a
 * final one, so a plausible wrong formula is presented as an answer.
 *
 * ## Why not `parseIncompleteMarkdown: false`
 *
 * Because the flag is global, and completion is the whole reason this
 * dependency was chosen. On this exact input set:
 *
 * | unclosed | flag on | flag off |
 * |---|---|---|
 * | `**important` | bold | plain |
 * | `` `foo( `` | code | plain |
 * | `[docs](` | link | plain |
 * | `$$O(n \log` | KATEX ← the defect | plain |
 *
 * Turning it off fixes one row by breaking three. So completion stays on and
 * the ONE construct where a premature guess is a lie gets neutralised here.
 *
 * ## How
 *
 * The last `$$` is escaped only when it opens a run nothing closes. Escaping
 * (rather than deleting) is what keeps the literal `$$` visible: the user sees
 * the characters the model has actually emitted, which is the honest state.
 */

/** The delimiter. Inline math uses the same one — `singleDollarTextMath` is off. */
const DELIMITER = "$$";

/**
 * Escape a trailing unclosed `$$`, leaving balanced math untouched.
 *
 * Fenced code is skipped: `` ```sh\necho $$ `` is a shell PID, not an opening
 * delimiter, and rewriting inside a fence would corrupt code the user copies.
 */
export function maskIncompleteMath(source: string): string {
  const segments = splitOnFences(source);
  let count = 0;

  // Count across prose segments only — a `$$` inside a fence closes nothing.
  for (const segment of segments) {
    if (segment.fenced) continue;
    count += occurrences(segment.text);
  }

  if (count % 2 === 0) return source;

  // Odd ⇒ the LAST prose `$$` is the unclosed opener.
  for (let i = segments.length - 1; i >= 0; i -= 1) {
    const segment = segments[i];
    if (!segment || segment.fenced) continue;
    const at = segment.text.lastIndexOf(DELIMITER);
    if (at === -1) continue;
    segments[i] = {
      fenced: false,
      text: `${segment.text.slice(0, at)}\\$\\$${segment.text.slice(at + DELIMITER.length)}`,
    };
    break;
  }

  return segments.map((segment) => segment.text).join("");
}

interface Segment {
  readonly fenced: boolean;
  readonly text: string;
}

function occurrences(text: string): number {
  let n = 0;
  let from = 0;
  for (;;) {
    const at = text.indexOf(DELIMITER, from);
    if (at === -1) return n;
    n += 1;
    from = at + DELIMITER.length;
  }
}

/**
 * Split into alternating prose and fenced-code segments.
 *
 * An UNCLOSED fence swallows the rest of the string — which is correct: while a
 * fence is open, everything after it is code, including any `$$`.
 */
function splitOnFences(source: string): Segment[] {
  const segments: Segment[] = [];
  const fence = /^[ \t]*(?:```|~~~)/gm;
  let cursor = 0;
  let open: number | null = null;

  for (let match = fence.exec(source); match !== null; match = fence.exec(source)) {
    const lineEnd = source.indexOf("\n", match.index);
    const after = lineEnd === -1 ? source.length : lineEnd + 1;

    if (open === null) {
      segments.push({ fenced: false, text: source.slice(cursor, match.index) });
      open = match.index;
      cursor = match.index;
    } else {
      segments.push({ fenced: true, text: source.slice(open, after) });
      open = null;
      cursor = after;
    }
  }

  // A fence left open owns everything to the end.
  segments.push({ fenced: open !== null, text: source.slice(cursor) });
  return segments;
}
