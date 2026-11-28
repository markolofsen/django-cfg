import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

const HERE = dirname(fileURLToPath(import.meta.url));

/**
 * `mermaid` unpacks to ~84 MB, and exactly one module imports it:
 * `hooks/useMermaidRenderer`, reached only through `Mermaid.client`'s dynamic
 * import. Nothing else asserts that. A convenient `export { Mermaid } from
 * './Mermaid.client'` added to the barrel typechecks, keeps every test green,
 * and puts the parser in every consumer's entry chunk.
 *
 * `./builders` matters more still: it is a pure string API a server pass or a
 * CLI can call, and a static edge from it to the renderer would make that
 * impossible for a reason nobody could see.
 */

const EXTERNAL = /^[^.]/;

function reachable(entry: string): Set<string> {
  const seen = new Set<string>();
  const queue = [entry];

  while (queue.length > 0) {
    const file = queue.pop();
    if (file === undefined || seen.has(file)) continue;
    seen.add(file);

    const source = readFileSync(file, 'utf8');
    // Static VALUE edges only: `import(...)` is the split itself, and
    // `import type` / `export type` erase. `[^;]*?` because a multi-line
    // `export {…} from` is the shape most barrels use.
    for (const match of source.matchAll(
      /(?:^|\n)\s*(?:import|export)\s+(type\s+)?[^;]*?from\s+'([^']+)'/g,
    )) {
      if (match[1] !== undefined) continue;
      const spec = match[2];
      if (spec === undefined || EXTERNAL.test(spec)) continue;
      const resolved = resolveSpec(file, spec);
      if (resolved !== null) queue.push(resolved);
    }
  }

  return seen;
}

function resolveSpec(from: string, spec: string): string | null {
  const base = resolve(dirname(from), spec);
  for (const candidate of [`${base}.ts`, `${base}.tsx`, join(base, 'index.ts'), join(base, 'index.tsx')]) {
    try {
      readFileSync(candidate, 'utf8');
      return candidate;
    } catch {
      continue;
    }
  }
  return null;
}

function importsMermaid(files: Set<string>): boolean {
  for (const file of files) {
    const source = readFileSync(file, 'utf8');
    for (const match of source.matchAll(/(?:^|\n)\s*import\s+([^;\n]*?)from\s+'mermaid'/g)) {
      if (!/^\s*type\s/.test(match[1] ?? '')) return true;
    }
  }
  return false;
}

describe('entries', () => {
  const root = reachable(join(HERE, 'index.tsx'));
  const builders = reachable(join(HERE, 'builders', 'index.ts'));

  it('keeps the parser out of the root entry', () => {
    expect(importsMermaid(root)).toBe(false);
  });

  it('keeps the parser out of the builders, which must run without a DOM', () => {
    expect(importsMermaid(builders)).toBe(false);
  });

  it('walks a graph big enough to mean something', () => {
    // A resolver that returned null for everything would pass both assertions
    // above forever.
    expect(root.size).toBeGreaterThan(15);
    expect(builders.size).toBeGreaterThan(10);
  });
});
