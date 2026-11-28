import type { Frame } from '../../wire/frames';
import type { ChatTransport } from '../../wire/transport';

/** One step of a scripted run: a frame after a pause, or an error thrown as a real transport would (refusal, network, lost stream). */
export type ScriptStep = { frame: Frame; after?: number } | { throw: Error; after?: number };

const pause = (ms: number, signal: AbortSignal) =>
  new Promise<void>((resolve) => {
    const timer = setTimeout(resolve, ms);
    signal.addEventListener('abort', () => {
      clearTimeout(timer);
      resolve();
    }, { once: true });
  });

/** A transport that replays a script: stories and tests drive the real adapter and session with it, so every state is the production code path. */
export function scriptedTransport(steps: ScriptStep[] | ((text: string) => ScriptStep[])): ChatTransport {
  return {
    async *open({ text, signal }) {
      for (const step of typeof steps === 'function' ? steps(text) : steps) {
        await pause(step.after ?? 40, signal);
        if (signal.aborted) return;
        if ('throw' in step) throw step.throw;
        yield step.frame;
      }
    },
  };
}
