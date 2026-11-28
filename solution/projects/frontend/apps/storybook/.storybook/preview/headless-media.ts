/**
 * Declare microphone capture unavailable — in the Vitest browser run only.
 *
 * Headless Chromium ships `navigator.mediaDevices.getUserMedia` but rejects
 * every call with `NotSupportedError`. Components that open a preview stream —
 * `VoiceControlMenu` via `useMicPreview` — therefore start async work that
 * fails AFTER the story's play function has finished, landing a console.warn
 * (and, as the timing shifts, an unhandled rejection) outside any test. That is
 * a failure whose message names neither the story nor the assertion, and it
 * comes and goes with machine load.
 *
 * Removing the method is more honest than resolving it with a fake stream: a
 * fake would animate the level meter in an environment with no microphone, so
 * the story would demonstrate something untrue. Absence is a state the speech
 * code already handles as a first-class case — every call site guards on
 * `navigator.mediaDevices?.getUserMedia` and renders the meter flat — so this
 * exercises a real supported path rather than inventing one.
 *
 * Gated on the Vitest browser flag, because in an interactive Storybook the
 * microphone is genuinely present and the live meter is the point of the
 * component. Applied at preview load, not per story: it is a property of the
 * environment, not state to reset between stories.
 */
export function disableMediaCaptureUnderTest(): void {
  // Set by @vitest/browser in the preview iframe; absent in `pnpm dev`.
  if (!('__vitest_browser__' in globalThis)) return;

  const mediaDevices = globalThis.navigator?.mediaDevices;
  if (!mediaDevices || !('getUserMedia' in mediaDevices)) return;

  // `delete` on the instance leaves the prototype method reachable, so shadow
  // it with an own `undefined` property instead.
  Object.defineProperty(mediaDevices, 'getUserMedia', {
    value: undefined,
    configurable: true,
    writable: true,
  });
}
