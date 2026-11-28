/**
 * @vitest-environment jsdom
 */
import * as React from 'react';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { describe, expect, it, vi } from 'vitest';

let currentPath = '/ru/';

vi.mock('next/navigation', () => ({
  usePathname: () => currentPath,
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn(), forward: vi.fn(), prefetch: vi.fn() }),
}));
vi.mock('next/link', () => ({ default: (props: Record<string, unknown>) => props.children ?? null }));

import { watchPathname } from '../usePathnameChange';
import { NextRouterAdapter } from './nextjs';

describe('NextRouterAdapter', () => {
  it('announces a Next pathname change to pathname watchers (Next navigates with its own captured pushState)', () => {
    window.history.replaceState(null, '', '/ru/');
    currentPath = '/ru/';
    const seen: string[] = [];
    const stop = watchPathname((path) => seen.push(path));
    const box = document.createElement('div');
    const root = createRoot(box);
    (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
    act(() => root.render(<NextRouterAdapter>x</NextRouterAdapter>));
    expect(seen).toEqual([]); // the first pathname is not a navigation

    // Next moved the URL without our patched pushState: only the adapter's pathname tells.
    act(() => {
      Object.getPrototypeOf(window.history).pushState.call(window.history, null, '', '/ru/watch/x/');
      currentPath = '/ru/watch/x/';
      root.render(<NextRouterAdapter>x</NextRouterAdapter>);
    });
    expect(seen).toEqual(['/ru/watch/x/']);
    stop();
    act(() => root.unmount());
  });
});
