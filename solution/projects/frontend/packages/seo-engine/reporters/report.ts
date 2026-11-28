/**
 * Human-readable report for `check`.
 */
import { relative } from 'node:path';
import pc from 'picocolors';
import type { BrokenReason, CheckResult, ExternalResult } from '../core/types.js';

const REASON_LABEL: Record<BrokenReason, string> = {
  'old-prefix': pc.magenta('old-prefix'),
  'absolute-wrong': pc.yellow('absolute-wrong'),
  'missing-page': pc.red('missing-page'),
  'bad-anchor': pc.blue('bad-anchor'),
  'missing-asset': pc.cyan('missing-asset'),
  'jsx-relative-href': pc.yellow('jsx-relative-href'),
  'missing-basepath': pc.red('missing-basepath'),
};

export function printCheckReport(result: CheckResult): void {
  const { scanned, links, broken } = result;

  if (broken.length === 0) {
    console.log(pc.green(`✓ ${links} internal links across ${scanned} files — all resolve.`));
    return;
  }

  // group by file
  const byFile = new Map<string, typeof broken>();
  for (const b of broken) {
    const arr = byFile.get(b.file) ?? [];
    arr.push(b);
    byFile.set(b.file, arr);
  }

  const cwd = process.cwd();
  for (const [file, items] of byFile) {
    console.log('\n' + pc.bold(pc.underline(relative(cwd, file))));
    items.sort((a, b) => a.line - b.line);
    for (const b of items) {
      const loc = pc.dim(`${b.line}:${b.column}`);
      const tag = REASON_LABEL[b.reason];
      const fix = b.suggestion
        ? `  ${pc.dim('->')} ${b.autoFixable ? pc.green(b.suggestion) : pc.dim('candidates: ' + b.suggestion)}`
        : '';
      console.log(`  ${loc}  ${tag}  ${pc.red(b.raw)}${fix}`);
    }
  }

  const auto = broken.filter((b) => b.autoFixable).length;
  const manual = broken.length - auto;
  console.log(
    '\n' +
      pc.red(`✗ ${broken.length} broken link(s)`) +
      pc.dim(` across ${byFile.size} file(s) — `) +
      pc.green(`${auto} auto-fixable`) +
      pc.dim(', ') +
      pc.yellow(`${manual} need review`),
  );
  console.log(pc.dim(`(scanned ${links} internal links in ${scanned} files)`));
}

/** Human-readable report for `external` (HTTP probe of outbound links). */
export function printExternalReport(result: ExternalResult): void {
  const { total, refs, dead } = result;

  if (dead.length === 0) {
    console.log(pc.green(`✓ ${total} external URLs (${refs} refs) — all reachable.`));
    return;
  }

  const cwd = process.cwd();
  const byFile = new Map<string, typeof dead>();
  for (const d of dead) {
    const arr = byFile.get(d.file) ?? [];
    arr.push(d);
    byFile.set(d.file, arr);
  }

  for (const [file, items] of byFile) {
    console.log('\n' + pc.bold(pc.underline(relative(cwd, file))));
    items.sort((a, b) => a.line - b.line);
    for (const d of items) {
      const loc = pc.dim(`${d.line}`);
      const status = d.status === 0 ? pc.red('ERR') : pc.red(String(d.status));
      const note = d.note ? pc.dim(` (${d.note})`) : '';
      console.log(`  ${loc}  ${status}  ${pc.red(d.url)}${note}`);
    }
  }

  console.log(
    '\n' +
      pc.red(`✗ ${dead.length} dead external URL(s)`) +
      pc.dim(` out of ${total} checked (${refs} refs across files)`),
  );
}
