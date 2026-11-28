import { spawnSync } from 'node:child_process';
import { join } from 'node:path';

/**
 * Source gates that run before anything is staged.
 *
 * They live here, not only in the Makefile, because `node
 * scripts/publish/cli.mjs publish` bypasses make entirely — a check somebody
 * has to remember to run is not a gate. Each is a fast standalone script (no
 * build, no registry) and a non-zero exit stops the publish.
 *
 * `--no-build` does NOT skip them: the defect they catch is in source, which
 * every tarball carries whether or not it was rebuilt.
 */
const GATES = [
  ['tailwind-var-syntax', 'scripts/check-tailwind-var-syntax.mjs'],
  ['widget-direction', 'scripts/check-widget-direction.mjs'],
];

/** Throws on the first failing gate, after printing its own output. */
export function runGates(rootDir) {
  for (const [name, script] of GATES) {
    const r = spawnSync(process.execPath, [join(rootDir, script)], { cwd: rootDir, stdio: 'inherit' });
    if (r.error) throw new Error(`gate ${name}: ${r.error.message}`);
    if (r.status !== 0) throw new Error(`gate ${name} failed — nothing published`);
  }
}
