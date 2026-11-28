import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

const HERE = dirname(fileURLToPath(import.meta.url));

/**
 * The split is the package's whole reason for two entries, and nothing else
 * asserts it: a `check-types` pass and a green test suite both survive an
 * `import { MapContainer } from './components'` added to the root barrel, and
 * the only symptom is ~800 KB in every consumer's entry chunk.
 *
 * So walk the STATIC import graph from each entry and look for the module
 * that pulls MapLibre GL. The lazy entry must not reach it; the eager one
 * must, or it is not doing its job either.
 */

const IGNORED = /^(react|react-dom|@djangocfg|@turf|lucide-react|pmtiles|react-map-gl|maplibre-gl)/;

function reachable(entry: string): Set<string> {
  const seen = new Set<string>();
  const queue = [entry];

  while (queue.length > 0) {
    const file = queue.pop();
    if (file === undefined || seen.has(file)) continue;
    seen.add(file);

    const source = readFileSync(file, 'utf8');
    // Static VALUE edges only. Two exclusions, both load-bearing:
    //   - `import(...)` is the split itself and must not count;
    //   - `import type` / `export type` erase, and counting them reports the
    //     container as reachable from the lazy entry through a props re-export
    //     that costs nothing.
    // `[^;]*?` rather than `[^;\n]*?`: a multi-line `export {\n A,\n B\n}
    // from '...'` is the shape most of the barrels use, and a line-bounded
    // pattern walks six modules and calls the graph clean.
    for (const match of source.matchAll(
      /(?:^|\n)\s*(?:import|export)\s+(type\s+)?[^;]*?from\s+'([^']+)'/g,
    )) {
      if (match[1] !== undefined) continue;
      const spec = match[2];
      if (spec === undefined || IGNORED.test(spec) || !spec.startsWith('.')) continue;
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

/**
 * Does this graph pull MapLibre GL in at RUNTIME?
 *
 * Not by looking for `from 'maplibre-gl'`: every module here imports that for
 * its TYPES, which erase, and the one true edge is a different specifier.
 * MapLibre arrives through `react-map-gl/maplibre`'s default export — the
 * `<Map>` component — and alongside it the stylesheet. Both are in `MapInner`,
 * and either one alone is the whole ~800 KB.
 */
function importsMapLibreAtRuntime(files: Set<string>): boolean {
  for (const file of files) {
    const source = readFileSync(file, 'utf8');
    if (/(?:^|\n)\s*import\s+'maplibre-gl\/dist\/maplibre-gl\.css'/.test(source)) return true;
    for (const match of source.matchAll(/(?:^|\n)\s*import\s+([^;\n]*?)from\s+'react-map-gl\/maplibre'/g)) {
      const clause = match[1] ?? '';
      if (/^\s*type\s/.test(clause)) continue;
      // A default import is the `<Map>` component, which loads the library.
      // The named ones (`Source`, `Layer`, `Marker`) are thin and do not.
      if (/^\s*[A-Za-z_$][\w$]*\s*(?:,|$)/.test(clause.trim())) return true;
    }
  }
  return false;
}

describe('entries', () => {
  const lazy = reachable(join(HERE, 'index.tsx'));
  const eager = reachable(join(HERE, 'eager.ts'));

  it('keeps MapLibre out of the default entry', () => {
    expect(importsMapLibreAtRuntime(lazy)).toBe(false);
  });

  it('pulls MapLibre into the eager entry, which is what it is for', () => {
    expect(importsMapLibreAtRuntime(eager)).toBe(true);
  });

  it('walks a graph big enough to mean something', () => {
    // A resolver that silently returned null for everything would pass both
    // assertions above forever — and a line-bounded specifier pattern already
    // did, walking 6 modules of the 53 this package has.
    expect(lazy.size).toBeGreaterThan(40);
  });

  it('makes the eager entry a superset, so an import cannot depend on which name it used', () => {
    for (const file of lazy) expect(eager.has(file)).toBe(true);
  });
});
