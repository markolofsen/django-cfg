// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';

import { computeLocator } from '../../page-snapshot/refs/locator';
import { RefRegistry } from '../../page-snapshot/refs/registry';
import { resolveRefs, type RefResolver } from './resolve-ref';
import type { CSTRefId } from './types';

afterEach(() => {
  document.body.innerHTML = '';
});

/** A tiny resolver backed by a plain map, for tests. */
function makeResolver(map: Record<string, HTMLElement | null>): RefResolver {
  return {
    resolve: (ref: CSTRefId) => map[ref] ?? null,
  };
}

describe('resolveRefs', () => {
  it('returns nothing without a resolver', () => {
    expect(resolveRefs(['@e1'], null)).toEqual([]);
  });

  it('resolves known refs to connected elements', () => {
    const el = document.createElement('button');
    document.body.appendChild(el);
    const resolver = makeResolver({ '@e1': el });

    const out = resolveRefs(['@e1'], resolver);
    expect(out).toHaveLength(1);
    expect(out[0]?.ref).toBe('@e1');
    expect(out[0]?.element).toBe(el);
  });

  it('drops refs the resolver does not know', () => {
    const resolver = makeResolver({});
    expect(resolveRefs(['@e9'], resolver)).toEqual([]);
  });

  it('drops elements detached from the DOM', () => {
    // Created but never appended — not connected.
    const orphan = document.createElement('div');
    const resolver = makeResolver({ '@e2': orphan });
    expect(resolveRefs(['@e2'], resolver)).toEqual([]);
  });

  it('resolves a batch, keeping only the live ones', () => {
    const live = document.createElement('a');
    document.body.appendChild(live);
    const orphan = document.createElement('a');
    const resolver = makeResolver({ '@e1': live, '@e2': orphan, '@e3': null });

    const out = resolveRefs(['@e1', '@e2', '@e3'], resolver);
    expect(out.map((o) => o.ref)).toEqual(['@e1']);
  });
});

describe('resolveRefs against a live RefRegistry', () => {
  it('resolves a ref after the captured node is recreated by a re-render', () => {
    // Capture: the snapshot registry stores a locator, not a node.
    const original = document.createElement('a');
    original.id = 'cta';
    original.textContent = 'Browse Catalog';
    document.body.appendChild(original);

    const registry = new RefRegistry('snap-1');
    registry.set('@e1', computeLocator(original, 'link'));

    // React re-render replaces the node with a fresh equivalent — the
    // original is now detached, exactly the production failure mode.
    original.remove();
    const fresh = document.createElement('a');
    fresh.id = 'cta';
    fresh.textContent = 'Browse Catalog';
    document.body.appendChild(fresh);

    const out = resolveRefs(['@e1'], registry);
    expect(out).toHaveLength(1);
    expect(out[0]?.element).toBe(fresh);
  });

  it('drops a ref whose element is genuinely gone', () => {
    const el = document.createElement('button');
    el.textContent = 'Delete';
    document.body.appendChild(el);

    const registry = new RefRegistry('snap-1');
    registry.set('@e1', computeLocator(el, 'button'));

    el.remove();
    expect(resolveRefs(['@e1'], registry)).toEqual([]);
  });
});
