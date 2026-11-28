/**
 * Streaming-markdown block splitter + boundary buffering.
 *
 * Purpose: render markdown LIVE during streaming without (a) re-parsing
 * the whole document on every token (O(n²)) and (b) flashing raw syntax
 * for half-written constructs. Approach (per plan105 §3.1 + §3.3):
 *
 *   1. Block-split: split accumulating markdown into top-level blocks at
 *      blank-line boundaries, RESPECTING fenced code blocks (a blank line
 *      inside ``` does NOT end the block). Each completed block has stable
 *      `raw` source, so the consumer can memoize blocks 0..N-1 and only
 *      re-parse the tail → ~O(n).
 *   2. Boundary buffering: the trailing block — the one still receiving
 *      tokens — is held back as RAW plain text until it reaches a safe
 *      boundary (a trailing newline). This kills the "flash of incomplete
 *      `**bold` / `[link](`" without any fragile syntax repair.
 *   3. Fence awareness: if the stream ends INSIDE an unclosed ``` fence,
 *      the tail is rendered as an in-progress code block (we virtually
 *      close the fence for that render only) instead of as broken markdown
 *      bleeding into the rest of the message.
 *
 * No `marked` / lexer dependency — a blank-line splitter that tracks fence
 * state is sufficient for the safe-80% path and adds zero deps. The actual
 * per-block rendering still goes through the full ReactMarkdown pipeline.
 *
 * This module is pure (no React) so it is trivially testable.
 */

/** A fenced-code-block opener: ``` or ~~~, optionally indented up to 3
 *  spaces, with an optional info string. Per CommonMark the closing fence
 *  must use the same char and be at least as long; we keep it simple and
 *  match the char + length, which covers real LLM output. */
const FENCE_RE = /^( {0,3})(`{3,}|~{3,})(.*)$/;

interface FenceState {
  open: boolean;
  /** The exact fence marker that opened the current block (e.g. "```"). */
  marker: string;
}

/** Does `line` open/close a fence given the current state? Returns the
 *  next fence state. A line that closes uses the same char, >= length, and
 *  no trailing info string. */
function stepFence(line: string, state: FenceState): FenceState {
  const m = FENCE_RE.exec(line);
  if (!m) return state;
  // Groups 2 and 3 are non-optional in FENCE_RE, so a match always fills them.
  const marker = m[2] ?? '';
  const info = (m[3] ?? '').trim();
  if (!state.open) {
    // Any fence line opens a block (info string allowed on open).
    return { open: true, marker };
  }
  // Inside a fence: a bare fence of the same char and >= length closes it.
  // Group 2 matches 3+ chars, so both markers are non-empty here; the `[0]`
  // reads compare `undefined` only for a state that can't occur.
  const sameChar = marker[0] === state.marker[0];
  const longEnough = marker.length >= state.marker.length;
  if (sameChar && longEnough && info === '') {
    return { open: false, marker: '' };
  }
  return state;
}

export interface SplitResult {
  /** Completed, stable top-level blocks (safe to memoize + parse). */
  blocks: string[];
  /** The trailing in-flight block, or '' if the content ended on a
   *  clean boundary. Held back from `blocks` so it can be rendered raw
   *  (boundary buffering) until it completes. */
  tail: string;
  /** True when `tail` is the body of an unterminated fenced code block —
   *  the consumer should render it as an in-progress code block rather
   *  than raw prose. */
  tailInOpenFence: boolean;
}

/**
 * Split `content` into stable blocks + a trailing in-flight block.
 *
 * Boundary rule: a block is "complete" once a blank line follows it AND
 * we are not inside an open fence. The text after the last such boundary
 * is the `tail`. If the whole content ends with a newline and no fence is
 * open, the tail is empty (everything promoted to stable blocks).
 *
 * @param content raw accumulated markdown (never mutated)
 */
export function splitStreamingBlocks(content: string): SplitResult {
  if (content.length === 0) {
    return { blocks: [], tail: '', tailInOpenFence: false };
  }

  const lines = content.split('\n');
  const blocks: string[] = [];
  let current: string[] = [];
  let fence: FenceState = { open: false, marker: '' };

  // Track fence state at the START of the current accumulating block so we
  // know, at the end, whether the tail is inside an open fence.
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line === undefined) continue;
    const wasOpen = fence.open;
    fence = stepFence(line, fence);

    const isBlank = line.trim() === '';
    // A blank line outside any fence is a block boundary. We only cut when
    // we have accumulated something — leading/again-blank lines collapse.
    if (isBlank && !fence.open && !wasOpen) {
      if (current.length > 0) {
        blocks.push(current.join('\n'));
        current = [];
      }
      // Drop the blank separator itself.
      continue;
    }
    current.push(line);
  }

  // Whatever remains is the in-flight tail. If the original content ended
  // with a trailing newline AND we're on a clean boundary (no open fence),
  // the tail is genuinely complete prose — but we still keep it as `tail`
  // unless it was already closed by a blank line above. To maximize stable
  // blocks, promote the tail to a completed block when it ends on a clean
  // newline boundary and no fence is open.
  let tail = current.join('\n');
  const tailInOpenFence = fence.open;

  if (!tailInOpenFence && tail.length > 0 && content.endsWith('\n')) {
    // Content ended on a newline and the tail isn't inside a fence — treat
    // it as a finished block so it parses (and memoizes) immediately.
    blocks.push(tail);
    tail = '';
  }

  return { blocks, tail, tailInOpenFence };
}

/**
 * Prepare the in-flight tail for rendering.
 *
 * - If the tail is inside an open fence, virtually close it so it renders
 *   as an in-progress code block (not raw text bleeding downward). The
 *   close is appended to a COPY — stored content is never mutated.
 * - Otherwise return the tail untouched; the consumer renders it as plain
 *   `whitespace-pre-wrap` text (boundary buffering — no syntax repair).
 *
 * NOTE: we deliberately do NOT auto-close dangling `**` / `[` / inline
 * backticks here (plan105 §3.2, deferred / flag-gated). The only fence we
 * close is the block code fence, because an unclosed block fence would
 * otherwise swallow the rest of the message and the close is unambiguous.
 */
export function renderableTail(
  tail: string,
  tailInOpenFence: boolean,
): { source: string; asCode: boolean } {
  if (!tailInOpenFence) return { source: tail, asCode: false };
  // Re-derive the opening fence marker so we close with a matching one.
  const firstLine = tail.split('\n', 1)[0] ?? '';
  const m = FENCE_RE.exec(firstLine);
  const marker = m?.[2] ?? '```';
  // Ensure the close sits on its own line.
  const needsNewline = !tail.endsWith('\n');
  return {
    source: `${tail}${needsNewline ? '\n' : ''}${marker}`,
    asCode: true,
  };
}
