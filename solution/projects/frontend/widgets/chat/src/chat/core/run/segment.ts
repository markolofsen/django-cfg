/**
 * Which parts of a message are one run.
 *
 * Adjacent thoughts, tool calls and trace steps form a run; text, a card or an
 * attachment ends it, so the answer is never pulled under a disclosure and the
 * order the turn happened in is kept. The run is a render-only `RunPart`, drawn by
 * the renderer a host registers under `run`.
 */

import type { MessagePart, RunPart } from "../conversation/parts";
import { stepOf } from "./view";

export type RunItem =
  | { readonly kind: "part"; readonly part: MessagePart }
  | { readonly kind: "run"; readonly part: RunPart };

const cache = new WeakMap<MessagePart, RunPart>();

const same = (a: readonly MessagePart[], b: readonly MessagePart[]): boolean => a.length === b.length && a.every((part, i) => part === b[i]);

/**
 * One `RunPart` per segment, reused while the segment's parts are the same objects.
 * The reducer keeps an unchanged part's identity, so a delta landing in the answer's
 * text does not re-render a settled run above it.
 */
function runOf(parts: readonly MessagePart[]): RunPart {
  const first = parts[0] as MessagePart;
  const known = cache.get(first);
  if (known !== undefined && same(known.parts, parts)) return known;
  const run: RunPart = { type: "run", id: `run:${first.id}`, parts };
  cache.set(first, run);
  return run;
}

export function planRuns(parts: readonly MessagePart[]): RunItem[] {
  const out: RunItem[] = [];
  let open: MessagePart[] = [];
  const close = (): void => {
    if (open.length > 0) out.push({ kind: "run", part: runOf(open) });
    open = [];
  };
  for (const part of parts) {
    if (stepOf(part) !== null) {
      open.push(part);
      continue;
    }
    close();
    out.push({ kind: "part", part });
  }
  close();
  return out;
}
