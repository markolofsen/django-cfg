/**
 * Publishing happens from a staged copy, never from the working tree:
 *
 *   1. copy each member to `<tmp>/<group>/<short>` (no node_modules/dist/.turbo)
 *   2. delete every `.*` and `@*` path inside the copy — `files` in package.json
 *      is a recursive whitelist and `.npmignore` is ignored inside whitelisted
 *      dirs, so `.claude/`, `@dev/`, `@sources/` would otherwise ship (they did,
 *      up to v2.1.294)
 *   3. rewrite `workspace:*` deps to a range npm can actually resolve
 *   4. build in the ORIGINAL dir (monorepo deps resolve there), copy `dist/` in
 *
 * The working tree keeps `workspace:*` throughout.
 */

import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';

import { log, run, runLive } from './ui.mjs';

const DEP_BLOCKS = ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies'];

export function stageDir(ws, member) {
  return join(ws.rootDir, ws.config.tmpDir, member.group, member.short);
}

/**
 * Copy every member into the stage and fix its manifest.
 *
 * `resolved` maps a package name to the version a dependant must ask for: the
 * version this run publishes, or — for a member that is skipped because it is
 * identical to npm — the version already on the registry. Writing the local
 * version instead is what made a skipped member unresolvable for everything
 * that depended on it.
 */
export function stage(ws, members, resolved) {
  const tmp = join(ws.rootDir, ws.config.tmpDir);
  rmSync(tmp, { recursive: true, force: true });
  mkdirSync(tmp, { recursive: true });

  for (const m of members) {
    const dest = stageDir(ws, m);
    cpSync(m.dir, dest, {
      recursive: true,
      filter: (src) => src === m.dir || !['node_modules', 'dist', '.turbo'].includes(src.split('/').pop()),
    });
    stripInternal(dest);
    rewriteDeps(dest, resolved);
  }
  return tmp;
}

/** `files` is a recursive whitelist, so internal directories must be deleted. */
function stripInternal(dir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.name.startsWith('.') || entry.name.startsWith('@')) rmSync(full, { recursive: true, force: true });
    else if (entry.isDirectory()) stripInternal(full);
  }
}

function rewriteDeps(dir, resolved) {
  const file = join(dir, 'package.json');
  const pkg = JSON.parse(readFileSync(file, 'utf8'));
  const unresolved = [];
  for (const block of DEP_BLOCKS) {
    for (const [dep, range] of Object.entries(pkg[block] ?? {})) {
      if (!String(range).startsWith('workspace:')) continue;
      const version = resolved.get(dep);
      if (!version) { unresolved.push(`${block}.${dep}`); continue; }
      pkg[block][dep] = `^${version}`;
    }
  }
  if (unresolved.length) {
    throw new Error(`${pkg.name}: workspace deps with no resolvable version: ${unresolved.join(', ')}`);
  }
  writeFileSync(file, `${JSON.stringify(pkg, null, 2)}\n`);
}

/**
 * Builds members that have a build script, in place, then copies dist/ in.
 *
 * Through turbo, in ONE invocation, so its cache applies: a package whose
 * inputs have not changed is restored instead of rebuilt. Calling `pnpm build`
 * inside each package ran tsup directly and bypassed the cache entirely, so
 * every retry after a failed publish paid the full build again.
 */
export async function build(ws, members) {
  const targets = members.filter((m) => m.hasBuild);
  if (!targets.length) return [];

  log.info(`Building ${targets.length} package(s) …`);
  const filters = targets.flatMap((m) => ['--filter', m.name]);
  const code = await runLive('pnpm', ['turbo', 'run', 'build', ...filters], { cwd: ws.rootDir });

  const failed = [];
  if (code !== 0) return targets.map((m) => m.name);

  for (const m of targets) {
    const dist = join(m.dir, 'dist');
    // A zero exit with no dist/ is a failure, not a no-op: `exports` point at
    // ./dist/, so npm would take a package that cannot be imported at all.
    if (!existsSync(dist) || !statSync(dist).isDirectory()) {
      log.err(`${m.name}: build succeeded but produced no dist/`);
      failed.push(m.name);
      continue;
    }
    cpSync(dist, join(stageDir(ws, m), 'dist'), { recursive: true });
  }
  return failed;
}

/**
 * `npm publish` from the stage.
 *
 * `ok` is NOT the exit code alone. npm prints `+ name@version` and exits 0 for
 * a publish it rejected with EOTP, so the output is checked for that too —
 * trusting the code is what let a release report eleven successes and land
 * eight.
 */
export async function publishOne(ws, member, { otp, dryRun, tag }) {
  const args = ['publish', '--access', 'public'];
  if (otp) args.push(`--otp=${otp}`);
  if (dryRun) args.push('--dry-run');
  if (tag) args.push('--tag', tag);

  const { code, out } = await run('npm', args, { cwd: stageDir(ws, member), timeout: 180_000 });
  const logDir = join(ws.rootDir, ws.config.tmpDir, 'logs');
  mkdirSync(logDir, { recursive: true });
  const logFile = join(logDir, `${member.short}.log`);
  writeFileSync(logFile, out);

  const rejected = /npm error code (EOTP|E4\d\d|EPUBLISHCONFLICT)/.test(out);
  return { member, ok: code === 0 && !rejected, log: relative(ws.rootDir, logFile), out };
}
