// @vitest-environment jsdom

import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, describe, expect, it } from 'vitest';

import { TreeRoot } from '../TreeRoot';

(globalThis as Record<string, unknown>).IS_REACT_ACT_ENVIRONMENT = true;

describe('TreeRoot empty semantics', () => {
  const mounted: Array<ReturnType<typeof createRoot>> = [];

  afterEach(() => {
    act(() => mounted.splice(0).forEach((root) => root.unmount()));
  });

  it('announces the empty state without exposing an invalid empty tree', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    mounted.push(root);

    act(() => {
      root.render(
        <TreeRoot<{ name: string }>
          data={[]}
          getItemName={(node) => node.data.name}
        />,
      );
    });

    expect(container.querySelector('[role="tree"]')).toBeNull();
    expect(container.querySelector('[data-tree-root]')?.hasAttribute('tabindex')).toBe(false);
    expect(container.querySelector('[role="status"]')?.textContent).toBe('Nothing to show');
  });
});

describe('TreeRow keeps its tree semantics while drag is enabled', () => {
  const mounted: Array<ReturnType<typeof createRoot>> = [];

  afterEach(() => {
    act(() => mounted.splice(0).forEach((root) => root.unmount()));
  });

  /**
   * `useDraggable().attributes` carries `role: 'button'`, `tabIndex: 0` and
   * `aria-disabled` alongside the descriptive aria. Spread whole onto the row
   * — which is what it was — it overwrites the row's own `role="treeitem"` and
   * the roving tabindex, so the tree announces as a list of buttons and every
   * row becomes a tab stop.
   *
   * tsc reported it as three duplicate props and nothing else did: the symptom
   * is only audible. This is that report made into a test.
   */
  it('does not let dnd-kit overwrite role or tabindex', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    mounted.push(root);

    act(() => {
      root.render(
        <TreeRoot<{ name: string }>
          data={[{ id: 'a', data: { name: 'a' } }]}
          getItemName={(node) => node.data.name}
          enableDnD
          adapter={{ move: async () => {} }}
        />,
      );
    });

    const row = container.querySelector('[data-tree-row]');
    expect(row).not.toBeNull();
    expect(row?.getAttribute('role')).toBe('treeitem');
    expect(row?.getAttribute('tabindex')).toBe('-1');
    // The descriptive half must still arrive, or drag loses its announcement.
    expect(row?.getAttribute('aria-roledescription')).toBe('draggable');
  });
});
