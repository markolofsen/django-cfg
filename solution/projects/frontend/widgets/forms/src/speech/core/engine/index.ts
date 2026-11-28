/**
 * Tiny event-bus helper shared by every engine. Lets engine authors avoid
 * re-implementing add/remove listener bookkeeping while keeping the
 * public `RecognitionEngine.on(...)` contract identical across engines.
 */

import type { EngineEventMap, Unsub } from '../../types';

type Listeners = {
  [K in keyof EngineEventMap]: Set<EngineEventMap[K]>;
};

export function createEngineBus(): {
  on: <K extends keyof EngineEventMap>(event: K, cb: EngineEventMap[K]) => Unsub;
  emit: <K extends keyof EngineEventMap>(
    event: K,
    ...args: Parameters<EngineEventMap[K]>
  ) => void;
  clear: () => void;
} {
  const listeners: Listeners = {
    partial: new Set(),
    final: new Set(),
    error: new Set(),
    state: new Set(),
  };

  return {
    on(event, cb) {
      const set = listeners[event] as Set<typeof cb>;
      set.add(cb);
      return () => {
        set.delete(cb);
      };
    },
    emit(event, ...args) {
      const set = listeners[event];
      for (const cb of set) {
        try {
          (cb as (...a: unknown[]) => void)(...(args as unknown[]));
        } catch {
          // listener errors are isolated — never break the engine loop
        }
      }
    },
    clear() {
      for (const key of Object.keys(listeners) as Array<keyof Listeners>) {
        listeners[key].clear();
      }
    },
  };
}
