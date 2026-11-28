/**
 * Fail a story that writes to `console.error` / `console.warn`.
 *
 * Why here and not in `vitest.config.ts`: that file had an `onConsoleLog`
 * interceptor meant to do exactly this, and it never ran once. In Vitest
 * browser mode the preview iframe's console is forwarded by Vite — the lines
 * reaching the terminal read `[vite] (client) [console.error] …` — and never
 * reaches `onConsoleLog`, which sees only the Node-side process streams. A
 * probe settled it: a deliberate `console.error` inside a play function printed
 * and the run still exited 0.
 *
 * Runs as a preview `afterEach`, which Storybook executes as part of the story's
 * own lifecycle (phase `afterEach`, before `finished`), so the failure is
 * attributed to the story that caused it. Throwing from the `beforeEach`
 * cleanup instead reports it against the NEXT story — observed, not assumed.
 *
 * A React key warning, a hydration mismatch, an act() warning and a failed
 * network call all arrive this way and all indicate a real defect; counting
 * them as passing is how they accumulate.
 */
import type { StoryContext } from '@storybook/nextjs-vite';

type ConsoleMethod = 'error' | 'warn';

const WATCHED: ConsoleMethod[] = ['error', 'warn'];

/**
 * Messages a correct story still emits, with the reason each is unavoidable.
 * Keep this empty when possible — an entry here is a defect nobody has to see.
 */
const ALLOWED: RegExp[] = [];

let captured: string[] = [];
let installed = false;

/**
 * Never throws. `String(arg)` does: an object with a null prototype has no
 * `toString`, so `String(Object.create(null))` is a TypeError, and a hostile
 * getter can throw anything. Those arrive for real — a null-prototype dict from
 * `JSON.parse`, an MSW mock, a config object — and a throw here happens INSIDE
 * the patched `console.error`, before the original call runs. The gate meant to
 * surface a defect would then hide it behind "Cannot convert object to
 * primitive value".
 */
function describe(arg: unknown): string {
  if (arg instanceof Error) return `${arg.name}: ${arg.message}`;
  try {
    return String(arg);
  } catch {
    // Last resort that cannot reach user code on the object itself.
    return Object.prototype.toString.call(arg);
  }
}

function format(args: unknown[]): string {
  return args.map(describe).join(' ');
}

function install(): void {
  if (installed) return;
  installed = true;

  for (const method of WATCHED) {
    const previous = console[method].bind(console) as (...args: unknown[]) => void;
    console[method] = (...args: unknown[]) => {
      // Print FIRST. Recording is best-effort instrumentation; the message
      // itself is what someone is trying to read, and it must survive any
      // failure in the code that observes it.
      previous(...args);
      try {
        const line = format(args);
        if (!ALLOWED.some((pattern) => pattern.test(line))) {
          captured.push(`console.${method}: ${line}`);
        }
      } catch {
        // A pattern that throws must not take the console with it.
        captured.push(`console.${method}: <unformattable arguments>`);
      }
    };
  }
}

/** Start recording. Preview `beforeEach`. */
export function beginConsoleCapture(): void {
  install();
  captured = [];
}

/**
 * Throw if the story wrote anything. Preview `afterEach`.
 *
 * Only under Vitest: in an interactive Storybook a console warning should stay
 * a console warning, not break the page someone is looking at.
 */
export function endConsoleCapture(context: StoryContext): void {
  if (captured.length === 0) return;

  const lines = captured.join('\n');
  captured = [];

  if (!('__vitest_browser__' in globalThis)) return;

  throw new Error(
    `Story "${context.id}" wrote to the console:\n${lines}\n\n` +
      'Fix the cause. If a message is genuinely unavoidable, add it to ALLOWED ' +
      'in .storybook/preview/console-gate.ts with the reason.',
  );
}
