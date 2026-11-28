// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';

import { en } from '../i18n/locales/en';
import { buildBuiltinSections } from './builtins';
import { DebugSection } from './DebugSection';

vi.mock('@djangocfg/api/auth', () => ({ useTimezone: () => ({}), useAuth: () => ({}) }));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let host: HTMLElement | null = null;
let root: Root | null = null;

beforeAll(() => {
  window.matchMedia = ((q: string) => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, dispatchEvent: () => false })) as typeof window.matchMedia;
});

afterEach(() => {
  act(() => root?.unmount());
  host?.remove();
  host = root = null;
  localStorage.clear();
});

describe('builtins.debug', () => {
  const ids = (debug?: boolean) =>
    buildBuiltinSections({ builtins: debug === undefined ? {} : { debug }, enableDeleteAccount: true, copy: en }).map((s) => s.id);

  it('is off by default, in development and production alike, and on only for an explicit true', () => {
    for (const nodeEnv of ['development', 'production']) {
      vi.stubEnv('NODE_ENV', nodeEnv);
      expect(ids()).not.toContain('debug');
      expect(ids(false)).not.toContain('debug');
      expect(ids(true)).toContain('debug');
    }
    vi.unstubAllEnvs();
  });
});

describe('DebugSection', () => {
  it('shows the live readout, flips the HUD switch (persisted) and resets the scroll on demand', async () => {
    host = document.createElement('div');
    document.body.appendChild(host);
    root = createRoot(host);
    await act(async () => root!.render(<DebugSection />));

    const readout = host.querySelector('[data-testid=viewport-readout]')!;
    expect(readout.textContent).toContain('innerHeight');
    expect(readout.textContent).toContain('--app-height');

    const toggle = host.querySelector<HTMLElement>('[role=switch]')!;
    expect(toggle.getAttribute('aria-checked')).toBe('false');
    await act(async () => toggle.click());
    expect(localStorage.getItem('viewportdebug')).toBe('small');
    expect(document.querySelector('[data-viewport-debug]')).toBeNull(); // drawn by UiProviders, not by the dialog
    expect(host.querySelector('[role=switch]')!.getAttribute('aria-checked')).toBe('true');

    const reset = [...host.querySelectorAll('button')].find((b) => b.textContent === en.debug.remeasureNow)!;
    expect(reset).toBeTruthy();
    await act(async () => reset.click());
  });
});
