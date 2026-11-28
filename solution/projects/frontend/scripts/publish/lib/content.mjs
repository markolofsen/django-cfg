/**
 * Has a package actually changed since its last release?
 *
 * Packs the local member and the published tarball and compares them file by
 * file. Two things in package.json are exempt — `version` and every
 * `@djangocfg/*` range — because the publisher rewrites both itself, so
 * including them would mark every package as changed on every run.
 *
 * `null` means "cannot tell" (never published, registry down, pack failed).
 * Callers publish on `null`: a needless publish costs a version number, a
 * wrongly skipped one ships nothing.
 */

import { publishedVersions } from './registry.mjs';
import { run } from './ui.mjs';

export async function contentChanged(member) {
  const versions = await publishedVersions(member.name);
  if (versions === null || versions.length === 0) return null;

  const { mkdtempSync, rmSync, readdirSync, readFileSync, existsSync } = await import('node:fs');
  const { join } = await import('node:path');
  const { tmpdir } = await import('node:os');

  const work = mkdtempSync(join(tmpdir(), 'pubdiff-'));
  try {
    const latest = versions[versions.length - 1];
    const got = await run('npm', ['pack', `${member.name}@${latest}`, '--pack-destination', work], { timeout: 120_000 });
    if (got.code !== 0) return null;
    const mine = await run('npm', ['pack', '--pack-destination', work], { cwd: member.dir, timeout: 120_000 });
    if (mine.code !== 0) return null;

    const tarballs = readdirSync(work).filter((f) => f.endsWith('.tgz'));
    if (tarballs.length !== 2) return null;
    const [a, b] = tarballs.map((f) => join(work, f));
    const dirs = [join(work, 'a'), join(work, 'b')];
    // Every npm tarball unpacks to `package/`, so extract into a private
    // directory each and strip that wrapper. BSD tar (macOS) has no
    // `--one-top-level`, so the directory is made first.
    const { mkdirSync } = await import('node:fs');
    for (const [i, t] of [a, b].entries()) {
      mkdirSync(dirs[i], { recursive: true });
      const r = await run('tar', ['xzf', t, '-C', dirs[i], '--strip-components=1'], { timeout: 60_000 });
      if (r.code !== 0) return null;
    }
    if (!dirs.every(existsSync)) return null;

    const list = (root) => {
      const out = [];
      const walk = (d, rel) => {
        for (const e of readdirSync(d, { withFileTypes: true }).sort((x, y) => x.name.localeCompare(y.name))) {
          const p = join(d, e.name);
          const r = rel ? `${rel}/${e.name}` : e.name;
          if (e.isDirectory()) walk(p, r); else out.push(r);
        }
      };
      walk(root, '');
      return out;
    };

    const [fa, fb] = dirs.map(list);
    if (fa.join('\n') !== fb.join('\n')) return true;

    // `version` and the scope's own ranges are the publisher's to rewrite.
    const normalise = (raw) => {
      const pkg = JSON.parse(raw);
      delete pkg.version;
      for (const block of ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies']) {
        for (const dep of Object.keys(pkg[block] ?? {})) {
          if (dep.startsWith('@djangocfg/')) pkg[block][dep] = '*';
        }
      }
      return JSON.stringify(pkg);
    };

    for (const f of fa) {
      const [x, y] = dirs.map((d) => join(d, f));
      if (f === 'package.json') {
        if (normalise(readFileSync(x, 'utf8')) !== normalise(readFileSync(y, 'utf8'))) return true;
      } else if (!readFileSync(x).equals(readFileSync(y))) {
        return true;
      }
    }
    return false;
  } catch {
    return null;
  } finally {
    rmSync(work, { recursive: true, force: true });
  }
}
