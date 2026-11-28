// @vitest-environment jsdom
import { act, createElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { PageSnapshotChip } from './page-snapshot-chip';
import { PageSnapshotProvider } from './provider';

(globalThis as Record<string, unknown>).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
});

afterEach(() => {
  act(() => root.unmount());
  container.remove();
});

async function render(defaultLinked: boolean) {
  await act(async () => {
    root.render(
      // `children` is a REQUIRED prop of PageSnapshotProviderProps, so the
      // positional form the rule asks for does not typecheck.
      // eslint-disable-next-line react/no-children-prop
      createElement(PageSnapshotProvider, {
        defaultLinked,
        children: createElement(PageSnapshotChip, {}),
      }),
    );
  });
}

describe('PageSnapshotChip', () => {
  it('renders nothing when not opted in', async () => {
    await render(false);
    expect(container.textContent).toBe('');
  });

  it('shows "Screen connected" when opted in', async () => {
    await render(true);
    expect(container.textContent).toContain('Screen connected');
  });

  it('exposes a preview button when opted in', async () => {
    await render(true);
    const previewBtn = container.querySelector(
      '[aria-label="Preview shared page context"]',
    );
    expect(previewBtn).not.toBeNull();
  });
});
