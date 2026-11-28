// @vitest-environment jsdom
import { act, createElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { PageSnapshotProvider } from './provider';
import {
  usePageSnapshotToggle,
  type PageSnapshotToggle,
} from './use-page-snapshot-toggle';

(globalThis as Record<string, unknown>).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;
let toggle: PageSnapshotToggle | null = null;

function Probe() {
  toggle = usePageSnapshotToggle();
  return null;
}

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
});

afterEach(() => {
  act(() => root.unmount());
  container.remove();
  toggle = null;
});

async function render() {
  await act(async () => {
    root.render(
      // `children` is a REQUIRED prop of PageSnapshotProviderProps, so the
      // positional form the rule asks for does not typecheck.
      // eslint-disable-next-line react/no-children-prop
      createElement(PageSnapshotProvider, {
        children: createElement(Probe),
      }),
    );
  });
}

describe('usePageSnapshotToggle', () => {
  it('starts not pressed', async () => {
    await render();
    expect(toggle!.pressed).toBe(false);
    expect(toggle!.label).toMatch(/share/i);
  });

  it('toggles the opt-in on and off', async () => {
    await render();

    await act(async () => toggle!.toggle());
    expect(toggle!.pressed).toBe(true);
    expect(toggle!.label).toMatch(/stop sharing/i);

    await act(async () => toggle!.toggle());
    expect(toggle!.pressed).toBe(false);
  });
});
