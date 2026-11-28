// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { LayoutI18nProvider } from '../../shared/LayoutI18nProvider';
import type { I18nLayoutConfig } from '../../layouts/types/layout.types';
import { LocaleSuggestion } from './LocaleSuggestion';
import { readMemory } from './memory';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let host: HTMLElement | null = null;
let root: Root | null = null;

const setLanguages = (languages: string[]) =>
  Object.defineProperty(navigator, 'languages', { value: languages, configurable: true });

async function mount(i18n: Partial<I18nLayoutConfig> = {}, delay = 1500) {
  const config: I18nLayoutConfig = {
    locale: 'en',
    locales: ['en', 'de', 'ar'],
    onLocaleChange: vi.fn(),
    ...i18n,
  };
  host = document.createElement('div');
  document.body.appendChild(host);
  root = createRoot(host);
  await act(async () =>
    root!.render(
      <LayoutI18nProvider value={config}>
        <LocaleSuggestion />
      </LayoutI18nProvider>,
    ),
  );
  await act(async () => {
    await vi.advanceTimersByTimeAsync(delay);
  });
  return config;
}

const card = () => document.querySelector<HTMLElement>('[data-locale-suggestion]');

beforeEach(() => {
  vi.useFakeTimers();
  localStorage.clear();
  setLanguages(['de-DE', 'en']);
});

afterEach(() => {
  act(() => root?.unmount());
  host?.remove();
  host = root = null;
  vi.useRealTimers();
});

describe('LocaleSuggestion', () => {
  it('shows nothing until the page has settled', async () => {
    await mount({}, 1000);
    expect(card()).toBeNull();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(600);
    });
    expect(card()).not.toBeNull();
  });

  it('speaks the browser language and names the target in its own language', async () => {
    await mount();
    expect(card()?.textContent).toContain('Deutsch');
    expect(card()?.textContent).toContain('Diese Seite ist in Deutsch verfügbar');
    expect(card()?.getAttribute('lang')).toBe('de-DE');
    expect(card()?.getAttribute('dir')).toBe('ltr');
  });

  it('is right-to-left for an Arabic browser', async () => {
    setLanguages(['ar']);
    await mount();
    expect(card()?.getAttribute('dir')).toBe('rtl');
  });

  it('switches on the primary button and does not remember it as a dismissal', async () => {
    const config = await mount();
    const button = [...card()!.querySelectorAll('button')].find((b) => b.textContent?.includes('Deutsch'))!;
    await act(async () => button.click());
    expect(config.onLocaleChange).toHaveBeenCalledWith('de');
    expect(card()).toBeNull();
  });

  it('remembers a dismissal for the pair and stays quiet on the next visit', async () => {
    await mount();
    await act(async () => card()!.querySelector<HTMLButtonElement>('[data-slot=banner-close]')!.click());
    expect(card()).toBeNull();
    expect(Object.keys(readMemory().dismissed)).toEqual(['de>en']);

    act(() => root?.unmount());
    host?.remove();
    await mount();
    expect(card()).toBeNull();
  });

  it('closes on Escape from inside the card', async () => {
    await mount();
    await act(async () => {
      card()!.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    });
    expect(card()).toBeNull();
    expect(readMemory().dismissed['de>en']).toBeTypeOf('number');
  });

  it('a one-language site mounts nothing: no listener, no storage read, no write', async () => {
    const listen = vi.spyOn(window, 'addEventListener');
    const read = vi.spyOn(Storage.prototype, 'getItem');
    const write = vi.spyOn(Storage.prototype, 'setItem');
    await mount({ locales: ['en'] });
    expect(card()).toBeNull();
    expect(listen.mock.calls.filter(([type]) => type === 'languagechange')).toEqual([]);
    expect(read).not.toHaveBeenCalled();
    expect(write).not.toHaveBeenCalled();
    expect(localStorage.length).toBe(0);
    listen.mockRestore();
    read.mockRestore();
    write.mockRestore();
  });

  it('can be turned off, and excluded by path', async () => {
    await mount({ suggestion: false });
    expect(card()).toBeNull();
    act(() => root?.unmount());
    host?.remove();
    window.history.pushState({}, '', '/legal/terms');
    await mount({ suggestion: { exclude: ['/legal'] } });
    expect(card()).toBeNull();
    window.history.pushState({}, '', '/');
  });

  it('shows nothing to automation', async () => {
    Object.defineProperty(navigator, 'webdriver', { value: true, configurable: true });
    await mount();
    expect(card()).toBeNull();
    Object.defineProperty(navigator, 'webdriver', { value: false, configurable: true });
  });
});
