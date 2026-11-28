#!/usr/bin/env node
/**
 * Publish `@djangocfg/*` to npm.
 *
 * The whole job in one sentence: work out each package's version, copy it to a
 * stage, build it, and run `npm publish`. Nothing waits on the registry.
 *
 * Two policies, from publish.config.mjs:
 *   synced       packages/*  — one version for the set; every member moves together
 *   independent  widgets/*   — own version; only published when its content changed
 *
 *   list     local vs npm
 *   plan     what publish would do — writes nothing
 *   bump     write versions only
 *   publish  bump, stage, build, publish
 *   pack     build tarballs into ~/.djangocfg-local for local consumers
 *   clean    remove the stage
 *
 *   --bump patch|minor|major|auto   --packages <kind>  --widgets <kind>
 *   --only a,b  --skip a,b  --group <name>  --tag <t>
 *   --all        publish widgets even when identical to npm
 *   --yes  --dry-run  --no-build  --keep-tmp  --otp <code>  --no-registry
 *
 * Three things this script exists to get right, each learned from a release
 * that went wrong:
 *
 *   1. An OTP is single-use. Sending one code with every package in a parallel
 *      run authenticates the first and fails the rest with EOTP — and npm still
 *      prints `+ name@version` and exits 0, so they looked published and were
 *      not. The code is only asked for when the account actually requires it
 *      (2FA mode `auth-and-writes`), and publishing is serial when one is used.
 *   2. npm's exit code is not the verdict. `publishOne` reads the output too.
 *   3. A dependant must name a version that EXISTS. For a skipped widget that
 *      is its published version, not the bumped local one.
 *   4. Source gates (lib/gates.mjs) run before `bump` and `publish`, dry run
 *      included. Tailwind 3's `-[--x]` compiles to an invalid declaration the
 *      browser drops; it shipped in ui-core 2.1.562 because nothing on this
 *      path looked at source.
 */

import { mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import config from '../../publish.config.mjs';
import { runGates } from './lib/gates.mjs';
import { isOnRegistry, isPublished, latestVersion, publishedVersions, whoami } from './lib/registry.mjs';
import { BUMPS, bump as bumpVersion, compare } from './lib/semver.mjs';
import { build, publishOne, stage, stageDir } from './lib/stage.mjs';
import { ask, c, log, mapLimit, run, table } from './lib/ui.mjs';
import { loadWorkspace, restoreVersionFiles, select, snapshotVersionFiles, writeVersion } from './lib/workspace.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');


// ── npm one-time password ────────────────────────────────────────────────────

const AUTH_ERROR = /EOTP|one-time password|E401|ENEEDAUTH|Unable to authenticate|two-factor authentication/i;

/** Get the owner's attention: a system sound and a notification (macOS), the terminal bell elsewhere. Never throws. */
function callOwner(message) {
  process.stdout.write('\x07');
  if (process.platform !== 'darwin') return;
  run('afplay', ['/System/Library/Sounds/Glass.aiff'], { timeout: 5_000 });
  run('osascript', ['-e', `display notification "${message.replace(/"/g, "'")}" with title "npm publish: enter your OTP"`], { timeout: 5_000 });
}

/** Sound, then ask for the code. Empty answer = no code (a login that needs none). */
async function askOtp(why) {
  callOwner(why);
  log.warn(why);
  const otp = await ask('npm OTP (a code lasts ~30 s; Enter to skip): ');
  return otp || undefined;
}

// ── plan ─────────────────────────────────────────────────────────────────────

function bumpKindFor(group, opts) {
  if (group.name === 'packages' && opts.packages) return opts.packages;
  if (group.name === 'widgets' && opts.widgets) return opts.widgets;
  return opts.bump;
}

/**
 * The target version of every member, and whether this run publishes it.
 * Writes nothing.
 */
async function makePlan(ws, opts) {
  const selected = new Set(select(ws, opts));
  const rows = [];

  for (const g of ws.groups) {
    const kind = bumpKindFor(g, opts);

    // A synced group moves as one, so its target is decided once, from the
    // master, and every member takes it whether or not its own files changed.
    let syncedTarget;
    if (g.versioning === 'synced') {
      syncedTarget = await targetFor(g.masterMember, kind, opts);
    }

    for (const m of g.members) {
      const isSelected = selected.has(m);
      const target = g.versioning === 'synced'
        ? syncedTarget
        : (isSelected ? await targetFor(m, kind, opts) : m.version);

      const onNpm = opts.registry ? await isPublished(m.name, target) : null;
      rows.push({ member: m, from: m.version, to: target, publish: isSelected, onNpm });
    }
  }
  return rows;
}

async function targetFor(member, kind, opts) {
  if (BUMPS.includes(kind)) return bumpVersion(member.version, kind);
  if (kind !== 'auto') return member.version;
  // `auto`: keep the local version if npm does not have it yet, else bump.
  const pub = await isPublished(member.name, member.version);
  if (pub === null) throw new Error(`Registry unreachable — cannot decide "auto" for ${member.name}`);
  return pub ? bumpVersion(member.version, 'patch') : member.version;
}

function printPlan(rows, opts) {
  table(
    rows.map((r) => {
      const version = r.from === r.to ? r.to : `${c.dim(r.from)} → ${c.bold(r.to)}`;
      let state;
      if (r.skipReason) state = c.dim(r.skipReason);
      else if (!r.publish) state = c.dim(r.from === r.to ? 'skip' : 'skip (version moves with group)');
      else if (r.onNpm === true) state = opts.dryRun ? c.yellow('left out: already on npm') : c.red('BLOCKED: already on npm');
      else if (r.onNpm === false) state = c.green(opts.dryRun ? 'publish (dry-run)' : 'publish');
      else state = c.yellow('publish (registry unknown)');
      return [c.dim(r.member.group), r.member.name, version, state];
    }),
    ['group', 'package', 'version', 'action'],
  );
}

// ── commands ─────────────────────────────────────────────────────────────────

async function cmdList(ws, opts) {
  const rows = await mapLimit(ws.members, 6, async (m) => {
    let latest = c.dim('—');
    let state = '';
    if (opts.registry) {
      const versions = await publishedVersions(m.name);
      if (versions === null) { latest = c.yellow('?'); state = c.yellow('registry unreachable'); }
      else if (!versions.length) { latest = c.dim('never'); state = c.cyan('unpublished'); }
      else {
        latest = versions.filter((v) => !v.includes('-')).sort(compare).at(-1) ?? versions.at(-1);
        const cmp = compare(m.version, latest);
        state = cmp === 0 ? c.green('published') : cmp > 0 ? c.cyan('ahead of npm') : c.red('behind npm');
      }
    }
    return [c.dim(m.group), m.name, m.version, latest, state, m.hasBuild ? c.dim('build') : ''];
  });
  table(rows, ['group', 'package', 'local', 'npm', 'state', '']);
  for (const g of ws.groups) {
    for (const s of g.skipped) log.info(`${c.dim(g.name)} ${s.short}: not published (${s.reason})`);
  }
}

async function cmdBump(ws, opts) {
  runGates(ROOT);
  if (opts.bump === 'none' && !opts.packages && !opts.widgets) {
    throw new Error('bump: say how — --bump patch|minor|major|auto, or --packages/--widgets per group');
  }
  const rows = await makePlan(ws, { ...opts, registry: false });
  const changes = rows.filter((r) => r.from !== r.to);
  if (!changes.length) { log.ok('Nothing to bump'); return; }
  for (const r of changes) writeVersion(r.member, r.to);
  log.head('Versions written');
  table(changes.map((r) => [c.dim(r.member.group), r.member.name, `${c.dim(r.from)} → ${c.bold(r.to)}`]));
}

async function cmdPublish(ws, opts) {
  // Before anything is written or staged, so a failed gate leaves the tree
  // untouched. A dry run is gated too — it is the rehearsal.
  runGates(ROOT);

  const user = await whoami();
  if (!user && !opts.dryRun) throw new Error('Not logged in to npm — run `npm login` (or use --dry-run)');
  log.ok(user ? `npm: ${user}` : 'npm: not logged in (dry-run continues without it)');

  const dirty = (await run('git', ['status', '--porcelain', '--', '.'], { cwd: ROOT })).out.trim();
  if (dirty) log.warn('Working tree has uncommitted changes — the version bump will land on top of them');

  const plan = await makePlan(ws, opts);

  // Skip a widget whose tarball would be identical to the published one:
  // republishing burns a version and makes every consumer re-resolve for no
  // change. A synced group is exempt — it carries one version by policy.
  if (!opts.all) {
    const { contentChanged } = await import('./lib/content.mjs');
    for (const r of plan.filter((x) => x.publish && x.member.versioning === 'independent')) {
      if (await contentChanged(r.member) === false) {
        r.publish = false;
        r.skipReason = 'skip: identical to npm';
        r.to = r.from;
      }
    }
  }

  const toPublish = plan.filter((r) => r.publish);
  if (!toPublish.length) throw new Error('Nothing to publish');

  log.head(`Plan${opts.dryRun ? ' (dry-run)' : ''}`);
  printPlan(plan, opts);

  const blocked = toPublish.filter((r) => r.onNpm === true);
  if (blocked.length && !opts.dryRun) {
    throw new Error(`${blocked.length} version(s) already on npm: ${blocked.map((r) => `${r.member.name}@${r.to}`).join(', ')} — pass --bump patch (or auto)`);
  }

  console.log('');
  // No y/N question: you ran publish, so you want it. A short countdown is the way out (Ctrl+C).
  if (!opts.yes) {
    const what = `${toPublish.length} package(s)${opts.dryRun ? ' [dry-run]' : ''}`;
    for (let left = 3; left > 0; left--) {
      process.stdout.write(`\rPublishing ${what} in ${left}s... (Ctrl+C to cancel) `);
      await new Promise((res) => setTimeout(res, 1000));
    }
    process.stdout.write('\r' + ' '.repeat(70) + '\r');
  }

  // What a dependant must ask for: the version that will be on the registry.
  const resolved = new Map();
  for (const r of plan) {
    resolved.set(r.member.name, r.publish ? r.to : (await latestVersion(r.member.name)) ?? r.from);
  }

  const versionChanges = plan.filter((x) => x.from !== x.to);
  const dryRunSnapshot = opts.dryRun ? snapshotVersionFiles(versionChanges.map((r) => r.member)) : null;

  // The staged copy needs the target versions, so the existing release path
  // rewrites working-tree manifests before staging. A dry-run must leave those
  // manifests byte-for-byte unchanged even when build or npm --dry-run fails.
  try {
    for (const r of versionChanges) writeVersion(r.member, r.to);

    const members = toPublish.map((r) => r.member);
    stage(ws, members, resolved);
    log.ok(`Staged ${members.length} package(s)`);

    if (opts.build) {
      const failed = await build(ws, members);
      if (failed.length) throw new Error(`Build failed: ${failed.join(', ')}`);
    } else {
      log.warn('--no-build: publishing whatever dist/ is already there');
    }

  // One OTP covers the whole parallel run (it is checked once per request window, not burnt by the first package).
  // It is asked for right after the build, with a sound, so you can walk away during the build. If npm rejects the
  // code (expired, mistyped), you are asked again and ONLY the failed packages are retried: no rebuild.
    const canAsk = !opts.dryRun && process.stdin.isTTY;
    let otp = opts.otp;
    if (!otp && canAsk) otp = await askOtp('Build finished: enter your npm one-time password to publish.');

    const byName = new Map();
    let pending = members;
    for (let round = 0; pending.length; round++) {
      const batch = await mapLimit(pending, 4, async (m) => {
        const r = await publishOne(ws, m, { otp, dryRun: opts.dryRun, tag: opts.tag });
        if (r.ok) log.ok(`${m.name}@${m.version}`);
        else log.err(`${m.name}@${m.version}  (${r.log})`);
        return r;
      });
      for (const r of batch) byName.set(r.member.name, r);
      const authFailed = batch.filter((r) => !r.ok && AUTH_ERROR.test(r.out));
      if (!authFailed.length || !canAsk || round >= 2) break;
      log.warn(`npm wants authentication for ${authFailed.length} package(s). Only those are retried.`);
      otp = await askOtp('npm rejected the code (expired or mistyped): enter a fresh one.');
      pending = authFailed.map((r) => r.member);
    }
    const results = members.map((m) => byName.get(m.name));

    const failed = results.filter((r) => !r.ok);
    if (failed.length) {
      if (failed.some((r) => /EOTP|one-time password/i.test(r.out))) {
        log.err('npm rejected these for a missing or expired one-time password.');
        log.warn('A code expires in ~30s — re-run and enter it when asked, or pass a fresh --otp.');
      }
      for (const r of failed) {
        console.log(c.red(`\n=== ${r.member.name} ===`));
        console.log(r.out.trim().split('\n').slice(-12).join('\n'));
      }
      log.warn(`Stage kept at ${ws.config.tmpDir} for inspection`);
      throw new Error(`${failed.length} of ${results.length} failed`);
    }

  // `npm publish` exiting 0 is not the registry serving the version. npm says so
  // itself — "Your package is being processed and may take a few minutes to
  // become available" — and on 2026-10-18/19 a package that npm accepted was
  // not visible for longer than a minute, twice, while its log ended "+ name@version".
  // So: ask the registry (uncached) for up to ~6 minutes, and if something is
  // still missing say it is PENDING, not failed. Re-publishing it would fail
  // with "cannot publish over the previously published version" and burn an OTP.
    if (!opts.dryRun && opts.registry) {
      let missing = members;
      for (let attempt = 0; attempt < 37 && missing.length; attempt++) {
        if (attempt) await new Promise((res) => setTimeout(res, 10_000));
        const seen = await mapLimit(missing, 4, async (m) => ((await isOnRegistry(m.name, m.version)) ? null : m));
        missing = seen.filter(Boolean);
      }
      if (missing.length) {
        log.warn(`Accepted by npm but not visible after ~6 min: ${missing.map((m) => `${m.name}@${m.version}`).join(', ')}`);
        log.warn('Do NOT re-publish — the version exists and a second publish is refused. Check later:');
        log.warn(`  npm view ${missing[0].name}@${missing[0].version} version --prefer-online`);
        log.warn(`Stage kept at ${ws.config.tmpDir} for inspection`);
        throw new Error(`${missing.length} of ${members.length} not yet visible on the registry`);
      }
      log.ok('All versions confirmed on the registry');
    }

    log.ok(`Published ${results.length} package(s)`);
    if (!opts.keepTmp) rmSync(join(ROOT, ws.config.tmpDir), { recursive: true, force: true });
  } finally {
    if (dryRunSnapshot) restoreVersionFiles(dryRunSnapshot);
  }
}

/**
 * `pack`: build every member exactly as `publish` would and write the tarballs to
 * `~/.djangocfg-local/` with a unique prerelease version, so a consumer can install
 * unpublished code through its own pnpm (peers resolve in the consumer: one React,
 * one copy of each package). Touches neither npm nor the working tree's versions.
 * The consumer side is `_map/django-cfg/djangocfg-local.mjs`.
 */
async function cmdPack(ws, opts) {
  runGates(ROOT);
  const members = select(ws, opts);
  const base = ws.groups[0].masterMember.version.split('-')[0];
  const version = `${base}-local.${Date.now()}`;
  const resolved = new Map(ws.members.map((m) => [m.name, m.version]));
  for (const m of members) resolved.set(m.name, version);

  stage(ws, members, resolved);
  for (const m of members) {
    const file = join(ws.rootDir, ws.config.tmpDir, m.group, m.short, 'package.json');
    const pkg = JSON.parse(readFileSync(file, 'utf8'));
    pkg.version = version;
    writeFileSync(file, `${JSON.stringify(pkg, null, 2)}\n`);
  }
  const failed = opts.build ? await build(ws, members) : [];
  if (failed.length) throw new Error(`Build failed: ${failed.join(', ')}`);

  const out = join(homedir(), '.djangocfg-local');
  mkdirSync(out, { recursive: true });
  for (const f of readdirSync(out)) if (f.endsWith('.tgz')) rmSync(join(out, f));
  const packages = {};
  for (const m of members) {
    const r = await run('npm', ['pack', '--pack-destination', out, '--silent'], { cwd: stageDir(ws, m), timeout: 180_000 });
    if (r.code !== 0) throw new Error(`${m.name}: npm pack failed\n${r.out}`);
    packages[m.name] = join(out, r.out.trim().split('\n').at(-1));
    log.ok(`${m.name}@${version}`);
  }
  writeFileSync(join(out, 'manifest.json'), `${JSON.stringify({ version, createdAt: new Date().toISOString(), packages }, null, 2)}\n`);
  rmSync(join(ROOT, ws.config.tmpDir), { recursive: true, force: true });
  log.ok(`Packed ${members.length} package(s) → ${out}`);
}

// ── args ─────────────────────────────────────────────────────────────────────

function parseArgs(argv) {
  const opts = { only: [], skip: [], bump: 'none', build: true, registry: true, keepTmp: false, dryRun: false, yes: false, all: false };
  const list = (v) => v.split(',').map((s) => s.trim()).filter(Boolean);
  let command;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => { const v = argv[++i]; if (v === undefined) throw new Error(`${a} needs a value`); return v; };
    if (!a.startsWith('--')) { if (command) throw new Error(`Unexpected argument "${a}"`); command = a; continue; }
    switch (a) {
      case '--bump': opts.bump = next(); break;
      case '--packages': opts.packages = next(); break;
      case '--widgets': opts.widgets = next(); break;
      case '--only': opts.only.push(...list(next())); break;
      case '--skip': opts.skip.push(...list(next())); break;
      case '--group': opts.group = next(); break;
      case '--otp': opts.otp = next(); break;
      case '--tag': opts.tag = next(); break;
      case '--all': opts.all = true; break;
      case '--yes': case '-y': opts.yes = true; break;
      case '--dry-run': opts.dryRun = true; break;
      case '--no-build': opts.build = false; break;
      case '--no-registry': opts.registry = false; break;
      case '--keep-tmp': opts.keepTmp = true; break;
      case '--help': case '-h': command = 'help'; break;
      default: throw new Error(`Unknown option "${a}"`);
    }
  }
  return { command: command ?? 'help', opts };
}

function help() {
  console.log(`
  publish  — @djangocfg/* to npm

  list     local vs npm            plan     what publish would do
  bump     write versions only     publish  bump, stage, build, publish
  pack     build tarballs into ~/.djangocfg-local (no npm, for local testing)
  clean    remove the stage

  --bump patch|minor|major|auto    --packages <kind>   --widgets <kind>
  --only a,b   --skip a,b   --group <name>   --tag <t>
  --all        publish widgets even when identical to npm
  --yes  --dry-run  --no-build  --keep-tmp  --otp <code>  --no-registry

  Widgets are versioned independently and are skipped when their content
  matches npm. Packages share one version and always move together.
`);
}

// ── main ─────────────────────────────────────────────────────────────────────

const { command, opts } = parseArgs(process.argv.slice(2));

try {
  if (command === 'help') { help(); process.exit(0); }
  const ws = loadWorkspace(ROOT, config);
  switch (command) {
    case 'list': await cmdList(ws, opts); break;
    case 'plan': printPlan(await makePlan(ws, opts), opts); break;
    case 'bump': await cmdBump(ws, opts); break;
    case 'publish': await cmdPublish(ws, opts); break;
    case 'pack': await cmdPack(ws, opts); break;
    case 'clean': rmSync(join(ROOT, config.tmpDir), { recursive: true, force: true }); log.ok('Stage removed'); break;
    default: throw new Error(`Unknown command "${command}"`);
  }
} catch (err) {
  log.err(err.message);
  process.exit(1);
}
