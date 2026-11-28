/**
 * Auto-fix safe broken links. Dry-run by default.
 *
 * Only `autoFixable` links (old-prefix with a real target, and unique slug relocations)
 * are rewritten. Ambiguous / missing links are reported but never touched.
 *
 * Rewrites operate on the exact authored `raw` href occurrence within the link's line,
 * so surrounding markdown/JSX is preserved.
 */
import { readFile, writeFile } from 'node:fs/promises';
import pc from 'picocolors';
import { checkLinks } from './check.js';
import type { BrokenLink, NextraSeoConfig } from '../core/types.js';

export interface FixChange {
  file: string;
  line: number;
  from: string;
  to: string;
}

export interface FixResult {
  changes: FixChange[];
  skipped: BrokenLink[];
  write: boolean;
}

export async function fixLinks(
  config: NextraSeoConfig,
  opts: { write: boolean } = { write: false },
): Promise<FixResult> {
  const { broken } = await checkLinks(config);

  const fixable = broken.filter((b) => b.autoFixable && b.suggestion && b.suggestion !== b.raw);
  const skipped = broken.filter((b) => !b.autoFixable);

  // group changes per file, apply line-by-line (replace first occurrence of `raw` on that line)
  const byFile = new Map<string, BrokenLink[]>();
  for (const b of fixable) {
    const arr = byFile.get(b.file) ?? [];
    arr.push(b);
    byFile.set(b.file, arr);
  }

  const changes: FixChange[] = [];

  for (const [file, items] of byFile) {
    const source = await readFile(file, 'utf8');
    const lines = source.split('\n');
    // apply deepest-first within a line isn't needed; we replace exact raw token once
    for (const item of items) {
      const idx = item.line - 1;
      if (idx < 0 || idx >= lines.length) continue;
      const to = item.suggestion!;
      if (lines[idx].includes(item.raw)) {
        lines[idx] = lines[idx].replace(item.raw, to);
        changes.push({ file, line: item.line, from: item.raw, to });
      }
    }
    if (opts.write && items.length) {
      await writeFile(file, lines.join('\n'));
    }
  }

  return { changes, skipped, write: opts.write };
}

export function printFixResult(result: FixResult): void {
  const { changes, write } = result;
  if (!changes.length) {
    console.log(pc.green('No auto-fixable links found.'));
  } else {
    const head = write ? pc.green(`Applied ${changes.length} fix(es):`) : pc.cyan(`${changes.length} fix(es) would be applied (dry-run):`);
    console.log(head);
    let cur = '';
    for (const c of changes) {
      if (c.file !== cur) {
        cur = c.file;
        console.log(pc.bold('\n  ' + c.file));
      }
      console.log(`    ${pc.dim('L' + c.line)}  ${pc.red(c.from)} ${pc.dim('->')} ${pc.green(c.to)}`);
    }
  }
  if (result.skipped.length) {
    console.log(pc.yellow(`\n${result.skipped.length} broken link(s) need manual review (ambiguous / no target).`));
  }
  if (!write && changes.length) {
    console.log(pc.dim('\nRun with --write to apply.'));
  }
}
