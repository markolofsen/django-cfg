import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline/promises';

const tty = process.stdout.isTTY && !process.env.NO_COLOR;
const paint = (code) => (s) => (tty ? `\x1b[${code}m${s}\x1b[0m` : String(s));

export const c = {
  green: paint(32),
  yellow: paint(33),
  red: paint(31),
  cyan: paint(36),
  dim: paint(2),
  bold: paint(1),
};

export const log = {
  info: (m) => console.log(c.cyan(m)),
  ok: (m) => console.log(c.green(`✓ ${m}`)),
  warn: (m) => console.log(c.yellow(`⚠ ${m}`)),
  err: (m) => console.error(c.red(`✗ ${m}`)),
  dim: (m) => console.log(c.dim(m)),
  head: (m) => console.log(`\n${c.bold(m)}`),
};

/** Fixed-width table without a dependency. Cells may carry ANSI colour. */
export function table(rows, headers) {
  const strip = (s) => String(s).replace(/\x1b\[[0-9;]*m/g, '');
  const all = headers ? [headers, ...rows] : rows;
  const widths = [];
  for (const row of all) row.forEach((cell, i) => { widths[i] = Math.max(widths[i] ?? 0, strip(cell).length); });
  const line = (row) => row.map((cell, i) => String(cell) + ' '.repeat(widths[i] - strip(cell).length)).join('  ');
  if (headers) {
    console.log(c.dim(line(headers)));
    console.log(c.dim(widths.map((w) => '─'.repeat(w)).join('  ')));
  }
  for (const row of rows) console.log(line(row));
}

export async function ask(question, { silent = false } = {}) {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    return (await rl.question(question)).trim();
  } finally {
    rl.close();
  }
}

export async function confirm(question) {
  const a = (await ask(`${question} (y/N) `)).toLowerCase();
  return a === 'y' || a === 'yes';
}

/** Runs a command, capturing output. Resolves `{ code, out }`; never throws on non-zero. */
export function run(cmd, args, { cwd, env, timeout } = {}) {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, { cwd, env: { ...process.env, ...env }, stdio: ['ignore', 'pipe', 'pipe'] });
    let out = '';
    child.stdout.on('data', (d) => { out += d; });
    child.stderr.on('data', (d) => { out += d; });
    let timer;
    if (timeout) timer = setTimeout(() => child.kill('SIGKILL'), timeout);
    child.on('close', (code) => { clearTimeout(timer); resolve({ code: code ?? 1, out }); });
    child.on('error', (e) => { clearTimeout(timer); resolve({ code: 1, out: String(e) }); });
  });
}

/** Runs a command with output streamed to the terminal. Resolves the exit code. */
export function runLive(cmd, args, { cwd } = {}) {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, { cwd, stdio: 'inherit' });
    child.on('close', (code) => resolve(code ?? 1));
    child.on('error', () => resolve(1));
  });
}

export async function mapLimit(items, limit, fn) {
  const results = new Array(items.length);
  let next = 0;
  async function worker() {
    while (next < items.length) {
      const i = next++;
      results[i] = await fn(items[i], i);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return results;
}
