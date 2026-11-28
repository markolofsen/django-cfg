import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { createWebSpeechEngine } from '../core/engine/webspeech';
import type { EngineState } from '../types';

/**
 * A minimal stand-in for the browser `SpeechRecognition` object. It records
 * the handlers the engine installs and lets a test drive the native
 * callbacks by hand, so we can reproduce Chrome's real misbehaviour:
 * firing `onerror` on a fast press→release WITHOUT a following `onend`.
 */
class FakeRecognition {
  lang = '';
  interimResults = false;
  continuous = false;
  maxAlternatives = 1;
  onstart: (() => void) | null = null;
  onend: (() => void) | null = null;
  onerror: ((e: { error: string; message?: string }) => void) | null = null;
  onresult: ((e: unknown) => void) | null = null;

  start = vi.fn();
  stop = vi.fn();
  abort = vi.fn();

  // Test helpers — simulate the native events.
  emitStart(): void {
    this.onstart?.();
  }
  emitEnd(): void {
    this.onend?.();
  }
  emitError(error: string): void {
    this.onerror?.({ error });
  }
}

describe('webspeech engine — terminal-state guarantees', () => {
  let fake: FakeRecognition;

  beforeEach(() => {
    fake = new FakeRecognition();
    // The engine reads `window.SpeechRecognition`. Node has no window, so
    // provide the constructor globals the engine's `resolveCtor` looks for.
    (globalThis as Record<string, unknown>).window = globalThis;
    (globalThis as Record<string, unknown>).SpeechRecognition = function () {
      return fake;
    } as unknown;
  });

  afterEach(() => {
    delete (globalThis as Record<string, unknown>).SpeechRecognition;
    delete (globalThis as Record<string, unknown>).webkitSpeechRecognition;
    delete (globalThis as Record<string, unknown>).window;
  });

  it('forces a `closed` state when the browser fires onerror without onend', async () => {
    const engine = createWebSpeechEngine();
    const states: EngineState[] = [];
    engine.on('state', (s) => states.push(s));

    await engine.start({ language: 'en-US', interim: true });
    fake.emitStart();
    expect(states).toContain('listening');

    // Chrome's fast press→release: an error, and then silence — NO onend.
    fake.emitError('no-speech');

    // The engine must synthesise `closed` so the consumer leaves the
    // transient state instead of hanging in the spinner.
    expect(states).toContain('closed');
  });

  it('does not emit `closed` twice when a trailing onend arrives after onerror', async () => {
    const engine = createWebSpeechEngine();
    const closes: number[] = [];
    engine.on('state', (s) => {
      if (s === 'closed') closes.push(1);
    });

    await engine.start({ language: 'en-US', interim: true });
    fake.emitStart();
    fake.emitError('aborted'); // forces close + teardown
    fake.emitEnd(); // Chrome sometimes DOES follow up — must be a no-op

    expect(closes).toHaveLength(1);
  });

  it('tears down after onerror so a subsequent start() actually runs', async () => {
    const engine = createWebSpeechEngine();
    await engine.start({ language: 'en-US', interim: true });
    fake.emitStart();
    expect(fake.start).toHaveBeenCalledTimes(1);

    fake.emitError('no-speech'); // teardown: instance is released

    // A fresh start must construct + start a new recognizer, not be
    // silently ignored because the dead instance was still held.
    await engine.start({ language: 'en-US', interim: true });
    expect(fake.start).toHaveBeenCalledTimes(2);
  });
});
