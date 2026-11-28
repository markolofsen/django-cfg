#!/usr/bin/env node
/**
 * `@stripe/*` may be imported only where this package says it may.
 *
 * THE DEFECT THIS CATCHES, because it already happened. The rule "@stripe/* is
 * touched in exactly two files" was stated in `src/index.ts`, in the README,
 * and in two file headers — and enforced nowhere. By 2026-09-20 it was false:
 * `components/appearance.ts` had acquired an `import type { Appearance }`.
 *
 * That import is harmless (types erase at compile time and pull nothing into a
 * bundle). The claim was not: four comments asserting an invariant that had
 * quietly stopped holding is how the next, real violation gets waved through.
 *
 * So the rule is now written once, here, executably — and it distinguishes the
 * two cases the prose could not:
 *
 *   VALUE import  → runtime dependency on the SDK. Two files.
 *   TYPE import   → compile-time only. One more file, for the appearance map.
 *
 * Adding a file to either list is a deliberate act. Widening VALUE especially:
 * it is what keeps the mock-only path Stripe-free in a consumer's bundle.
 */

import { readdirSync, readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SRC = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'src');

/** Files that may depend on the SDK at RUNTIME. */
const VALUE_ALLOWED = new Set([
  'transport/stripe-adapter.ts',
  'components/StripePaymentElement.tsx',
]);

/** Files that may additionally name SDK TYPES (erased at compile time). */
const TYPE_ALLOWED = new Set([...VALUE_ALLOWED, 'components/appearance.ts']);

/**
 * `import … from '@stripe/x'`, `export … from '@stripe/x'`, `import('@stripe/x')`.
 *
 * The `m` flag rather than a literal `\n`: `^` must match the first line of a
 * file too, and a file whose last line carries no trailing newline must not
 * shift what the anchor lines up with.
 */
const IMPORT = /^[^\S\n]*(import|export)\s+([\s\S]*?)from\s*['"](@stripe\/[^'"]+)['"]|import\s*\(\s*['"](@stripe\/[^'"]+)['"]\s*\)/gm;

function sourceFiles(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) {
      out.push(...sourceFiles(full));
    } else if (/\.tsx?$/.test(entry) && !entry.endsWith('.stories.tsx')) {
      out.push(full);
    }
  }
  return out;
}

const violations = [];

for (const file of sourceFiles(SRC)) {
  const relative = path.relative(SRC, file).split(path.sep).join('/');
  const source = readFileSync(file, 'utf8');

  for (const match of source.matchAll(IMPORT)) {
    const [, keyword, clause, from, dynamic] = match;
    const specifier = from ?? dynamic;
    // A dynamic import is always a value import; a static one is type-only
    // when the `type` keyword leads the clause (`import type { X }`) — a
    // clause-level `{ type X }` still loads the module, so it counts as value.
    const typeOnly = Boolean(from) && /^\s*type\s/.test(clause ?? '');
    const allowed = typeOnly ? TYPE_ALLOWED : VALUE_ALLOWED;

    if (!allowed.has(relative)) {
      violations.push({
        file: relative,
        specifier,
        kind: typeOnly ? 'type' : 'value',
        keyword: keyword ?? 'import()',
      });
    }
  }
}

if (violations.length > 0) {
  console.error(`x ${violations.length} disallowed @stripe/* import(s):`);
  for (const v of violations) {
    console.error(`    ${v.file}  (${v.kind} ${v.keyword})  ${v.specifier}`);
  }
  console.error('');
  console.error('  A VALUE import makes the SDK a runtime dependency of that file,');
  console.error('  which is what keeps mock-only bundles Stripe-free. Route it through');
  console.error('  the adapter seam, or add the file to VALUE_ALLOWED deliberately');
  console.error('  in scripts/check-stripe-imports.mjs.');
  process.exit(1);
}

console.log(
  `@stripe imports ok: ${VALUE_ALLOWED.size} value file(s), ` +
    `${TYPE_ALLOWED.size - VALUE_ALLOWED.size} type-only file(s), no others.`,
);
