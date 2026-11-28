// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from 'vitest';

import { isManifestMissing, MANIFEST_HINT, PWA_META_SCRIPT } from './pwaMeta';

const meta = (n: string) => document.head.querySelector(`meta[name="${n}"]`)?.getAttribute('content');
const run = () => new Function(PWA_META_SCRIPT)();

describe('PWA_META_SCRIPT', () => {
  beforeEach(() => {
    document.head.innerHTML = '';
  });

  it('adds viewport-fit=cover to an existing viewport and the iOS app tags', () => {
    document.head.innerHTML = '<meta name="viewport" content="width=device-width, initial-scale=1">';
    run();
    expect(meta('viewport')).toBe('width=device-width, initial-scale=1, viewport-fit=cover');
    expect(meta('apple-mobile-web-app-capable')).toBe('yes');
    expect(meta('mobile-web-app-capable')).toBe('yes');
    expect(meta('apple-mobile-web-app-status-bar-style')).toBe('black-translucent');
  });

  it('creates a viewport when none exists', () => {
    run();
    expect(meta('viewport')).toContain('viewport-fit=cover');
  });

  it('never overrides what the app set', () => {
    document.head.innerHTML =
      '<meta name="viewport" content="width=device-width, viewport-fit=contain">' +
      '<meta name="apple-mobile-web-app-status-bar-style" content="default">';
    run();
    expect(meta('viewport')).toBe('width=device-width, viewport-fit=contain');
    expect(meta('apple-mobile-web-app-status-bar-style')).toBe('default');
  });
});

describe('isManifestMissing', () => {
  beforeEach(() => {
    document.head.innerHTML = '';
  });

  it('is true without a manifest link', () => {
    expect(isManifestMissing(document)).toBe(true);
  });

  it('is false with a manifest link', () => {
    document.head.innerHTML = '<link rel="manifest" href="/manifest.webmanifest">';
    expect(isManifestMissing(document)).toBe(false);
  });

  it('is false without a document (SSR / bare test env)', () => {
    expect(isManifestMissing(undefined)).toBe(false);
    expect(isManifestMissing(null)).toBe(false);
  });

  it('hint names the supported import path only', () => {
    expect(MANIFEST_HINT).toContain('@djangocfg/nextjs/pwa/manifest');
  });
});
