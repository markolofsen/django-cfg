/**
 * What npm knows about a package. Reads only — nothing here waits.
 *
 * The publisher used to block after each publish until the registry served the
 * new version. That wait was removed: npm indexes within a minute or two on its
 * own, nothing downstream reads the registry during a release, and the wait hid
 * the real failure (see `publish` in cli.mjs) behind minutes of silence.
 */

import { run } from './ui.mjs';

const cache = new Map();

/**
 * Published versions, oldest first. `[]` when never published — npm answers
 * E404 for that, which is a fact, not a failure. `null` when the registry could
 * not be reached, so callers can tell "no versions" from "no answer".
 */
export async function publishedVersions(name) {
  if (cache.has(name)) return cache.get(name);
  const { code, out } = await run('npm', ['view', name, 'versions', '--json'], { timeout: 20_000 });
  let result = null;
  if (code === 0) {
    try {
      const parsed = JSON.parse(out);
      result = Array.isArray(parsed) ? parsed : [parsed];
    } catch {
      result = null;
    }
  } else if (/E404|404 Not Found|is not in this registry/i.test(out)) {
    result = [];
  }
  cache.set(name, result);
  return result;
}

export async function isPublished(name, version) {
  const versions = await publishedVersions(name);
  return versions === null ? null : versions.includes(version);
}

/**
 * Whether `name@version` is on the registry RIGHT NOW. Uncached, unlike
 * `publishedVersions`: that one is for planning, this one is for checking a
 * result. `null` means no answer, not "missing".
 */
export async function isOnRegistry(name, version) {
  const { code, out } = await run('npm', ['view', `${name}@${version}`, 'version', '--prefer-online'], { timeout: 20_000 });
  if (code === 0) return out.trim() === version;
  return /E404|404 Not Found|No match found/i.test(out) ? false : null;
}

export async function latestVersion(name) {
  const versions = await publishedVersions(name);
  return versions?.length ? versions[versions.length - 1] : null;
}

/** npm account name, or null when not logged in. */
export async function whoami() {
  const { code, out } = await run('npm', ['whoami'], { timeout: 15_000 });
  return code === 0 ? out.trim() : null;
}
