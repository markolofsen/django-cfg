/**
 * Auth trace: a persisted record of what the auth layer did, readable after any reload or redirect.
 *
 * Why storage and not `window`: a sign-in problem usually ends in a reload or a redirect, which throws away
 * everything held in memory and in the console. The events live in `localStorage` (falling back to
 * `sessionStorage`, then memory), so the next page can still print them. `window.__cfgAuth` is only the reader.
 *
 * Read it in the browser console, on any page of the origin, even after the redirect:
 *
 *   __cfgAuth.dump()    // copy-ready text with a header; paste it into the report
 *   __cfgAuth.trace()   // the raw array
 *   __cfgAuth.clear()   // empty it before reproducing
 *   __cfgAuth.copy()    // dump to the clipboard; __cfgAuth.download() saves the raw JSON
 *
 * What is recorded is the decision, never the secret: no token, code, address, cookie value or password.
 * Values are primitives, strings are cut, and keys that look sensitive are dropped (`SENSITIVE`).
 */

type Primitive = string | number | boolean | null;
export type TraceFields = Record<string, Primitive>;

export interface TraceEntry {
  /** Wall clock, ms since epoch. */
  t: number;
  /** ms since this page started (`performance.now()`), so a reload shows as the counter restarting. */
  p: number;
  /** Short random id of this page load: one sequence, several loads, told apart by this. */
  tab: string;
  ev: string;
  f?: TraceFields;
  /** Times this exact event repeated back to back (absent = once). A loop must not push the start of the chain out of the buffer. */
  n?: number;
}

const KEY = 'cfg.auth.trace';
const MAX = 200;
const MAX_STRING = 120;
const SENSITIVE = /token|otp|code|email|password|secret|cookie|authorization|key|identifier/i;

// One id per page load, shared by every copy of this module on the page (a second copy must not look like a second tab).
const TAB: string = (() => {
  const g = globalThis as Record<string, unknown>;
  return (g.__cfgAuthTab ??= Math.random().toString(36).slice(2, 6)) as string;
})();
const hasWindow = typeof window !== 'undefined';

let memory: TraceEntry[] = [];
let loaded = false;

function backend(): Storage | null {
  if (!hasWindow) return null;
  for (const name of ['localStorage', 'sessionStorage'] as const) {
    try {
      const s = window[name];
      s.setItem('__cfg_probe', '1');
      s.removeItem('__cfg_probe');
      return s;
    } catch {
      /* try the next one */
    }
  }
  return null;
}

function load(): TraceEntry[] {
  if (loaded) return memory;
  loaded = true;
  try {
    const raw = backend()?.getItem(KEY);
    const parsed: unknown = raw ? JSON.parse(raw) : [];
    if (Array.isArray(parsed)) memory = parsed.filter((e): e is TraceEntry => typeof e === 'object' && e !== null);
  } catch {
    memory = [];
  }
  return memory;
}

function persist(): void {
  try {
    backend()?.setItem(KEY, JSON.stringify(memory));
  } catch {
    /* quota or blocked storage: the in-memory copy still serves this page */
  }
}

function clean(fields?: TraceFields): TraceFields | undefined {
  if (!fields) return undefined;
  const out: TraceFields = {};
  for (const [k, v] of Object.entries(fields)) {
    if (SENSITIVE.test(k)) continue;
    if (typeof v === 'string') out[k] = v.length > MAX_STRING ? `${v.slice(0, MAX_STRING)}…` : v;
    else if (typeof v === 'number' || typeof v === 'boolean' || v === null) out[k] = v;
  }
  return Object.keys(out).length ? out : undefined;
}

/** Re-read storage before every write: another tab (or another copy) may have appended since this one last looked. */
function refresh(): void {
  try {
    const raw = backend()?.getItem(KEY);
    const parsed: unknown = raw ? JSON.parse(raw) : null;
    if (Array.isArray(parsed)) memory = parsed.filter((e): e is TraceEntry => typeof e === 'object' && e !== null);
  } catch {
    /* keep the in-memory copy */
  }
}

function record(at: number, ev: string, fields?: TraceFields): void {
  load();
  refresh();
  const entries = memory;
  const p = hasWindow && typeof performance !== 'undefined' ? Math.round(performance.now()) : 0;
  const f = clean(fields);
  const last = entries[entries.length - 1];
  if (last && last.tab === TAB && last.ev === ev && JSON.stringify(last.f) === JSON.stringify(f)) {
    last.n = (last.n ?? 1) + 1;
    last.t = at;
    last.p = p;
    persist();
    return;
  }
  entries.push({ t: at, p, tab: TAB, ev, f });
  if (entries.length > MAX) entries.splice(0, entries.length - MAX);
  persist();
}

/** Record one auth event. Safe anywhere: it never throws and does nothing on the server. */
export function authTrace(ev: string, fields?: TraceFields): void {
  if (!hasWindow) return;
  try {
    record(Date.now(), ev, fields);
  } catch {
    /* tracing never breaks auth */
  }
}

/** The recorded events, oldest first. */
/** @internal for tests */
export function resetAuthTraceForTests(): void {
  memory = [];
  loaded = true;
}

export function readAuthTrace(): TraceEntry[] {
  return load().slice();
}

/** Empty the trace. */
export function clearAuthTrace(): void {
  memory = [];
  loaded = true;
  try {
    backend()?.removeItem(KEY);
  } catch {
    /* ignore */
  }
}

function context(): string[] {
  if (!hasWindow) return [];
  const copies = (globalThis as Record<string, unknown>).__cfgAuthCopies ?? 1;
  const lines = [`url: ${window.location.href.split('?')[0]}`, `copies: ${String(copies)}`, `online: ${navigator.onLine}`, `ua: ${navigator.userAgent}`];
  try {
    const auth = (globalThis as Record<string, unknown>).__cfgAuthNow as (() => TraceFields) | undefined;
    const now = auth?.();
    if (now) lines.push(`now: ${Object.entries(now).map(([k, v]) => `${k}=${String(v)}`).join(' ')}`);
  } catch {
    /* the live state is a courtesy */
  }
  return lines;
}

/** Copy-ready text: a short header, then one line per event. Reloads show as a new `[tab]`. */
export function dumpAuthTrace(): string {
  const entries = load();
  const first = entries[0]?.t ?? Date.now();
  const rows = entries.map((e) => {
    const fields = e.f ? ` ${Object.entries(e.f).map(([k, v]) => `${k}=${String(v)}`).join(' ')}` : '';
    const at = new Date(e.t).toISOString().slice(11, 23);
    return `${at} +${String(e.t - first).padStart(6)}ms [${e.tab} p${e.p}] ${e.ev}${fields}${e.n && e.n > 1 ? ` x${e.n}` : ''}`;
  });
  return [`# cfg auth trace, ${entries.length} events`, ...context(), '', ...rows].join('\n');
}

/**
 * Install the reader. Called once from the package entry; idempotent across copies of this module.
 * The generated auth store forwards through `globalThis.__cfgAuthTrace` and queues until this runs.
 */
export function installAuthTrace(): void {
  if (!hasWindow) return;
  const g = globalThis as Record<string, unknown>;
  g.__cfgAuthTrace = authTrace;
  g.__cfgAuth = {
    trace: readAuthTrace,
    dump: () => {
      const text = dumpAuthTrace();
       
      console.log(text);
      return text;
    },
    clear: clearAuthTrace,
    /** Put the dump on the clipboard (works when the console output is blocked or too long to select). */
    copy: () => {
      const text = dumpAuthTrace();
      void navigator.clipboard?.writeText(text);
      return `${text.split('\n').length} lines copied`;
    },
    /** Download the raw trace as a JSON file. */
    download: () => {
      const blob = new Blob([JSON.stringify(readAuthTrace(), null, 1)], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `auth-trace-${Date.now()}.json`;
      a.click();
    },
  };
  const queued = g.__cfgAuthTraceQ;
  if (Array.isArray(queued)) {
    g.__cfgAuthTraceQ = [];
    for (const item of queued) {
      if (Array.isArray(item) && typeof item[1] === 'string') {
        try {
          record(Number(item[0]) || Date.now(), item[1], item[2] as TraceFields | undefined);
        } catch {
          /* ignore */
        }
      }
    }
  }
}

/**
 * Count the copies of this package in the page. More than one means the bundle holds duplicates (pnpm peer-set
 * variants, a dual ESM/CJS load): the contexts are shared (`sharedContext`), but the build should still be fixed.
 * Visible as `dup.copy` in the trace and once in the console.
 * Called once by the auth entry (`src/auth/index.ts`), not by this module (see below).
 */
export function registerAuthCopy(): void {
  if (!hasWindow) return;
  const g = globalThis as Record<string, unknown>;
  const n = ((g.__cfgAuthCopies as number | undefined) ?? 0) + 1;
  g.__cfgAuthCopies = n;
  if (n > 1) {
    authTrace('dup.copy', { copies: n });
    if (n === 2) {
       
      console.warn('[@djangocfg/api] more than one copy of the auth package is loaded; see __cfgAuth.dump() (dup.copy). Align the peer set so pnpm installs one instance.');
    }
  }
}
// NOT called here: `src/index.ts` and `src/auth/index.ts` are separate bundles that each carry this module, so
// counting at load made every healthy page report `copies: 2`. `src/auth/index.ts` (the client entry, which holds
// the contexts that must be single) calls `registerAuthCopy()`, so only a second copy of that entry counts.

// The reader is installed as soon as the package loads, so a trace exists from the first event.
installAuthTrace();
