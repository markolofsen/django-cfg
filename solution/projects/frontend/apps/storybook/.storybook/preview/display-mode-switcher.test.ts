import { describe, expect, it } from 'vitest';

import { resolveDevice, resolveEmulatedMode } from './display-mode-switcher';

describe('display mode emulation guard', () => {
  it('auto and unknown values never emulate', () => {
    expect(resolveEmulatedMode('auto', false)).toBeNull();
    expect(resolveEmulatedMode(undefined, false)).toBeNull();
  });
  it('desktop honours an explicit emulated choice', () => {
    expect(resolveEmulatedMode('standalone', false)).toBe('standalone');
    expect(resolveEmulatedMode('browser', false)).toBe('browser');
  });
  it('a real touch device is never emulated, even with a deep link', () => {
    expect(resolveEmulatedMode('standalone', true)).toBeNull();
  });
});

describe('device switch', () => {
  it('off keeps the story globals', () => {
    expect(resolveDevice('off', null, 'standalone', 'iphone')).toEqual({ displayMode: 'standalone', safeArea: 'iphone' });
    expect(resolveDevice(undefined, null, undefined, undefined)).toEqual({ displayMode: undefined, safeArea: undefined });
  });
  it('browser, pwa and auto override the finer items', () => {
    expect(resolveDevice('pwa', null, 'auto', 'none')).toEqual({ displayMode: 'standalone', safeArea: 'iphone' });
    expect(resolveDevice('browser', null, 'standalone', 'iphone')).toEqual({ displayMode: 'browser', safeArea: 'none' });
    expect(resolveDevice('auto', null, 'standalone', 'iphone')).toEqual({ displayMode: 'auto', safeArea: 'none' });
  });
  it('the URL parameter wins over the toolbar', () => {
    expect(resolveDevice('off', 'pwa', undefined, undefined)).toEqual({ displayMode: 'standalone', safeArea: 'iphone' });
  });
});
