import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

/**
 * The renderer must not be in a consumer's first paint.
 *
 * `beautiful-mermaid` is ~2.5 MB, and most transcripts never carry a diagram.
 * The whole reason the parser was chosen over the 84 MB runtime is that the
 * cost is small enough to be worth paying WHEN a diagram appears — which only
 * holds while nothing pulls it in beforehand.
 *
 * This gate exists because that guarantee was broken the first time the
 * component was wired: `renderMediaContent` is reachable from `chat`'s package
 * root, so a static `import { Diagram }` put the parser into every transcript.
 * Nothing failed — the only visible symptom was a module-loading test drifting
 * past its timeout, which reads as a slow machine.
 *
 * Walked as a STATIC graph rather than observed at runtime: "which module
 * imports which" is a fact about the source, and a runtime probe answers it
 * only if the loader happens to expose its registry. The first version of this
 * file guessed at that registry, saw nothing, and passed both cases against an
 * empty string — its control is what caught it, and is why one is kept below.
 */

const HERE = import.meta.dirname;
const PARSER = 'beautiful-mermaid';

/**
 * What a consumer actually imports.
 *
 * `index.ts` leads, because it is the subpath every consumer names and the one
 * place the split can be undone by a single re-export — which is how it was
 * undone the first time: the barrel listed the eager `Diagram` beside the lazy
 * one, and a barrel re-export is a static edge like any other. A gate that
 * checked only the leaf files reported that graph clean.
 */
const DEFERRED_ENTRIES = ['index.ts', 'lazy.tsx', 'plugin.ts'] as const;

describe('the parser is not in the entry graph', () => {
  it.each(DEFERRED_ENTRIES)('%s does not reach the parser statically', (entry) => {
    expect(staticGraph(entry)).not.toContain(PARSER);
  });

  it('detects the parser when a module DOES import it eagerly', () => {
    // The control. Without it these assertions pass on a walker that resolves
    // nothing, which is exactly how the previous version of this gate failed.
    expect(staticGraph('render.ts')).toContain(PARSER);
  });

  it('reaches through a re-export rather than stopping at the first file', () => {
    // The second control. `diagram.tsx` imports `./render`, so a walker that
    // only read one file's own imports would miss the parser here and report
    // the eager component deferred.
    expect(staticGraph('diagram.tsx')).toContain(PARSER);
  });
});

// `import type` / `export type` are excluded by the negative lookahead: they
// are erased before anything runs, so they cost a reader nothing. Keeping them
// would flag `lazy.tsx`, whose only tie to the eager component is its props
// type — and the fix would be to lose the type, which is worse than the leak.
const STATIC_IMPORT =
  /(?:^|\n)\s*(?:import|export)\s+(?!type\s)[\s\S]{0,400}?from\s+["']([^"']+)["']/g;

/**
 * Every bare dependency a file reaches through STATIC imports, transitively.
 *
 * `await import()` is deliberately not matched: deferring the parser behind one
 * is the whole mechanism under test, so counting it would make the fix
 * indistinguishable from the defect.
 */
function staticGraph(entry: string, seen = new Set<string>()): string[] {
  if (seen.has(entry)) return [];
  seen.add(entry);

  const source = readFileSync(join(HERE, entry), 'utf8');
  const found: string[] = [];

  for (const [, spec] of source.matchAll(STATIC_IMPORT)) {
    if (spec === undefined) continue;
    if (!spec.startsWith('.')) {
      found.push(spec);
      continue;
    }
    const local = resolveLocal(spec);
    if (local !== null) found.push(...staticGraph(local, seen));
  }

  return found;
}

/** A relative specifier as a filename in this folder, or null if it leaves it. */
function resolveLocal(spec: string): string | null {
  const name = spec.replace(/^\.\//, '');
  if (name.includes('/')) return null;
  for (const extension of ['.ts', '.tsx']) {
    try {
      readFileSync(join(HERE, name + extension));
      return name + extension;
    } catch {
      // Not this extension; try the next.
    }
  }
  return null;
}
