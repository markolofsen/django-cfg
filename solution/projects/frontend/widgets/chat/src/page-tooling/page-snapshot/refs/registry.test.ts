// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';

import { computeLocator } from './locator';
import { RefRegistry } from './registry';

afterEach(() => {
  document.body.innerHTML = '';
});

describe('RefRegistry', () => {
  it('reports unknown refs as unresolved', () => {
    const reg = new RefRegistry('snap-1');
    expect(reg.has('@e9')).toBe(false);
    expect(reg.resolve('@e9')).toBeNull();
    expect(reg.size).toBe(0);
    expect(reg.snapshotId).toBe('snap-1');
  });

  it('resolves a registered ref to its element', () => {
    const el = document.createElement('button');
    el.textContent = 'Save';
    document.body.appendChild(el);

    const reg = new RefRegistry('snap-1');
    reg.set('@e1', computeLocator(el, 'button'));

    expect(reg.has('@e1')).toBe(true);
    expect(reg.resolve('@e1')).toBe(el);
    expect(reg.size).toBe(1);
  });

  it('resolves after the original node is replaced by a re-render', () => {
    // Capture against the original node.
    const original = document.createElement('a');
    original.id = 'browse';
    original.textContent = 'Browse Catalog';
    document.body.appendChild(original);

    const reg = new RefRegistry('snap-1');
    reg.set('@e1', computeLocator(original, 'link'));

    // React re-render: the node is recreated as a fresh, equivalent one.
    original.remove();
    const fresh = document.createElement('a');
    fresh.id = 'browse';
    fresh.textContent = 'Browse Catalog';
    document.body.appendChild(fresh);

    const resolved = reg.resolve('@e1');
    expect(resolved).toBe(fresh);
    expect(resolved).not.toBe(original);
  });

  it('returns null when the element is genuinely gone', () => {
    const el = document.createElement('button');
    el.textContent = 'Delete';
    document.body.appendChild(el);

    const reg = new RefRegistry('snap-1');
    reg.set('@e1', computeLocator(el, 'button'));

    el.remove();
    expect(reg.resolve('@e1')).toBeNull();
  });

  it('exposes the stored locator for diagnostics', () => {
    const el = document.createElement('a');
    el.textContent = 'Home';
    document.body.appendChild(el);

    const reg = new RefRegistry('snap-1');
    reg.set('@e1', computeLocator(el, 'link'));

    const locator = reg.getLocator('@e1');
    expect(locator?.role).toBe('link');
    expect(locator?.name).toBe('Home');
    expect(reg.getLocator('@e9')).toBeUndefined();
  });
});
