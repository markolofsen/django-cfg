/**
 * Test setup: forget the runtime's shared page state.
 *
 * The session, handlers and API origin live on `globalThis` (`runtime/state.ts`), so they outlive
 * `vi.resetModules()` by design: that is what lets two copies of the module share one store. A test that wants a
 * fresh page deletes the slots too, as `smoke/harness.ts` does.
 */
export function resetRuntimeSlots(): void {
  const holder = globalThis as unknown as Record<symbol, unknown>;
  for (const name of ['djangocfg.api.auth', 'djangocfg.api.runtime']) delete holder[Symbol.for(name)];
}
