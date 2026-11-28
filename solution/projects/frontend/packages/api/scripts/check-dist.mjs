#!/usr/bin/env node
/**
 * Fails when dist/ holds a file that no package entry reaches.
 *
 * tsup writes into dist/ without removing what an earlier build left there, a
 * turbo cache hit restores outputs over whatever is already in dist/, and the
 * publisher copies dist/ into the stage as it is. @djangocfg/api@2.1.663
 * shipped 72 chunk files (and their 72 maps) that none of its entries load.
 *
 * The walk starts at every target in package.json `exports` (plus `main`,
 * `module`, `types`) and follows, from each file it reaches:
 *   - relative `import`/`export ... from`/`import()`/`require()` specifiers
 *     (JS) and relative imports and `/// <reference path>` (declarations);
 *   - the file's `sourceMappingURL`;
 *   - the declaration TypeScript looks up beside a JS file
 *     (x.mjs -> x.d.mts, x.cjs -> x.d.cts, x.js -> x.d.ts).
 * Any file under dist/ the walk does not reach is reported, as is an export
 * target that does not exist. Either one exits 1.
 *
 * Node built-ins only: it also runs as `prepublishOnly` inside the publish
 * stage, which has no node_modules.
 *
 * Usage: node scripts/check-dist.mjs [packageDir]
 */
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const pkgDir = resolve(process.argv[2] ?? join(dirname(fileURLToPath(import.meta.url)), '..'));
const distDir = join(pkgDir, 'dist');
const pkg = JSON.parse(readFileSync(join(pkgDir, 'package.json'), 'utf8'));
const rel = (p) => relative(pkgDir, p).split(sep).join('/');

if (!existsSync(distDir) || !statSync(distDir).isDirectory()) {
  console.error(`check-dist: ${rel(distDir)}/ does not exist; run the build first`);
  process.exit(1);
}

function targets(node, out) {
  if (typeof node === 'string') out.push(node);
  else if (Array.isArray(node)) for (const n of node) targets(n, out);
  else if (node && typeof node === 'object') for (const n of Object.values(node)) targets(n, out);
  return out;
}

const roots = [
  ...new Set(
    targets(pkg.exports, [pkg.main, pkg.module, pkg.types, pkg.typings].filter(Boolean))
      .map((p) => resolve(pkgDir, p))
      .filter((p) => p.startsWith(distDir + sep)),
  ),
];

const JS = /\.(mjs|cjs|js)$/;
const DTS = /\.d\.(ts|mts|cts)$/;
const JS_SPEC = /(?:\bfrom\s*|\bimport\s*\(\s*|\brequire\s*\(\s*|\bimport\s+)(['"])(\.{1,2}\/[^'"\n]+)\1/g;
const REF_PATH = /\/\/\/\s*<reference\s+path\s*=\s*(['"])([^'"\n]+)\1/g;
const SOURCE_MAP = /[#@]\s*sourceMappingURL=([^\s'"*]+)/g;
const SIBLING_DTS = { mjs: 'd.mts', cjs: 'd.cts', js: 'd.ts' };

const isFile = (p) => existsSync(p) && statSync(p).isFile();
const firstFile = (candidates) => candidates.find(isFile);

function resolveJs(from, spec) {
  const base = resolve(dirname(from), spec);
  return firstFile([base, ...['.mjs', '.cjs', '.js'].flatMap((e) => [base + e, join(base, `index${e}`)])]);
}

function resolveDts(from, spec) {
  const base = resolve(dirname(from), spec);
  if (DTS.test(base)) return firstFile([base]);
  const stem = base.replace(/\.(mjs|cjs|js|ts|mts|cts)$/, '');
  const ext = base.match(/\.(mjs|cjs|js)$/)?.[1];
  const preferred = ext ? [`${stem}.${SIBLING_DTS[ext]}`] : [];
  return firstFile([...preferred, `${stem}.d.ts`, `${stem}.d.mts`, `${stem}.d.cts`, join(stem, 'index.d.ts')]);
}

const reached = new Set();
const missingRoots = [];
const dangling = [];
const queue = [...roots];

for (const root of roots) if (!isFile(root)) missingRoots.push(root);

while (queue.length) {
  const file = queue.pop();
  if (reached.has(file) || !isFile(file)) continue;
  reached.add(file);

  const isDts = DTS.test(file);
  if (!isDts && !JS.test(file)) continue;
  const code = readFileSync(file, 'utf8');
  const next = [];

  for (const [, , spec] of code.matchAll(JS_SPEC)) {
    const hit = isDts ? resolveDts(file, spec) : resolveJs(file, spec);
    if (hit) next.push(hit);
    else dangling.push(`${rel(file)} -> ${spec}`);
  }
  if (isDts) {
    for (const [, , spec] of code.matchAll(REF_PATH)) {
      const hit = resolveDts(file, spec);
      if (hit) next.push(hit);
    }
  }
  for (const [, url] of code.matchAll(SOURCE_MAP)) {
    if (!url.startsWith('data:')) next.push(resolve(dirname(file), url));
  }
  if (!isDts) {
    const ext = file.match(JS)[1];
    next.push(file.replace(JS, `.${SIBLING_DTS[ext]}`));
  }
  for (const n of next) if (n.startsWith(distDir + sep) && !reached.has(n)) queue.push(n);
}

function listFiles(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? listFiles(join(dir, e.name)) : [join(dir, e.name)],
  );
}

const all = listFiles(distDir);
const unreached = all.filter((f) => !reached.has(f)).sort();

for (const d of dangling) console.warn(`check-dist: warning: relative import resolves to no file: ${d}`);

if (missingRoots.length || unreached.length) {
  for (const m of missingRoots) console.error(`check-dist: export target missing: ${rel(m)}`);
  if (unreached.length) {
    const shown = 20;
    console.error(
      `check-dist: ${unreached.length} of ${all.length} files in ${rel(distDir)}/ are reached by no entry ` +
        '(stale output of an earlier build?). Rebuild from an empty dist/: `pnpm build`.',
    );
    for (const f of unreached.slice(0, shown)) console.error(`  ${rel(f)}`);
    if (unreached.length > shown) console.error(`  ... and ${unreached.length - shown} more`);
  }
  process.exit(1);
}

console.log(`check-dist: ${all.length} files in ${rel(distDir)}/, all reached from ${roots.length} export targets`);
