import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';

/**
 * Discovers the publishable members of every group in `publish.config.mjs`.
 *
 * A member is `{ group, dir, name, short, version, pkg, hasBuild }` where
 * `short` is the directory name — what `--only`/`--skip` match against, so a
 * widget is `ogimage`, not `@djangocfg/widget-ogimage` (though that matches
 * too). `pkg` is the parsed package.json.
 */
export function loadWorkspace(rootDir, config) {
  const groups = config.groups.map((g) => {
    const dir = resolve(rootDir, g.dir);
    if (!existsSync(dir)) throw new Error(`Group "${g.name}": directory ${g.dir}/ not found`);
    const members = readdirSync(dir, { withFileTypes: true })
      .filter((e) => e.isDirectory() && !e.name.startsWith('.') && !e.name.startsWith('@'))
      .map((e) => readMember(g, join(dir, e.name), e.name))
      .filter(Boolean)
      .sort((a, b) => a.short.localeCompare(b.short));
    const group = { ...g, path: dir, members, skipped: [] };
    group.skipped = readdirSync(dir, { withFileTypes: true })
      .filter((e) => e.isDirectory() && !e.name.startsWith('.') && !e.name.startsWith('@'))
      .map((e) => ({ short: e.name, reason: reasonToSkip(join(dir, e.name)) }))
      .filter((s) => s.reason);
    if (g.versioning === 'synced') {
      group.masterMember = members.find((m) => m.short === g.master);
      if (!group.masterMember) throw new Error(`Group "${g.name}": master "${g.master}" is not a publishable member`);
    }
    return group;
  });
  const members = groups.flatMap((g) => g.members);
  const byName = new Map(members.map((m) => [m.name, m]));
  return { rootDir, config, groups, members, byName };
}

function reasonToSkip(dir) {
  const file = join(dir, 'package.json');
  if (!existsSync(file)) return 'no package.json';
  const pkg = JSON.parse(readFileSync(file, 'utf8'));
  if (pkg.private) return 'private';
  if (!pkg.name || !pkg.version) return 'no name/version';
  return null;
}

function readMember(group, dir, short) {
  if (reasonToSkip(dir)) return null;
  const pkg = JSON.parse(readFileSync(join(dir, 'package.json'), 'utf8'));
  return {
    group: group.name,
    versioning: group.versioning,
    dir,
    short,
    name: pkg.name,
    version: pkg.version,
    pkg,
    hasBuild: Boolean(pkg.scripts?.build),
  };
}

/** Rewrites only the `version` field, preserving the file's formatting. */
export function writeVersion(member, version) {
  const file = join(member.dir, 'package.json');
  const raw = readFileSync(file, 'utf8');
  const next = raw.replace(/("version"\s*:\s*")[^"]+(")/, `$1${version}$2`);
  if (next === raw) throw new Error(`${member.name}: could not find "version" in package.json`);
  writeFileSync(file, next);
  member.version = version;
  member.pkg.version = version;
}

/**
 * Capture package manifests before a command temporarily rewrites versions.
 * Keeping the original bytes matters because package.json files may contain
 * formatting or ordering that should not be normalised by a dry-run.
 */
export function snapshotVersionFiles(members) {
  return members.map((member) => {
    const file = join(member.dir, 'package.json');
    return { file, raw: readFileSync(file, 'utf8') };
  });
}

/** Restore manifests captured by snapshotVersionFiles. */
export function restoreVersionFiles(snapshot) {
  for (const { file, raw } of snapshot) writeFileSync(file, raw);
}

/**
 * Resolves `--only` / `--skip` selectors. A selector matches a member's
 * directory name, full package name, or package name without scope (with or
 * without a `widget-` prefix); `group:<name>` matches a whole group.
 */
export function matches(member, selector) {
  const s = selector.trim();
  if (!s) return false;
  if (s.startsWith('group:')) return member.group === s.slice(6);
  const bare = member.name.replace(/^@[^/]+\//, '');
  return [member.short, member.name, bare, bare.replace(/^widget-/, '')].includes(s);
}

export function select(ws, { only = [], skip = [], group } = {}) {
  const unknown = [...only, ...skip].filter((s) => !s.startsWith('group:') && !ws.members.some((m) => matches(m, s)));
  if (unknown.length) throw new Error(`Unknown package selector(s): ${unknown.join(', ')}. Run "list" to see names.`);
  return ws.members.filter((m) => {
    if (group && m.group !== group) return false;
    if (only.length && !only.some((s) => matches(m, s))) return false;
    if (skip.some((s) => matches(m, s))) return false;
    return true;
  });
}
