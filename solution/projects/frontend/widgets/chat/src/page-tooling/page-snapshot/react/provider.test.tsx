// @vitest-environment jsdom
import { act } from 'react';
import { createElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { PageSnapshotProvider } from './provider';
import {
  usePageSnapshot,
  type PageSnapshotContextValue,
} from './use-page-snapshot';

// React 19 act() environment flag.
(globalThis as Record<string, unknown>).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;
/** Latest context value, captured by the probe component each render. */
let ctx: PageSnapshotContextValue | null = null;

/** Probe component — publishes the context value to the test. */
function Probe() {
  ctx = usePageSnapshot();
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
  ctx = null;
});

/** Render the provider with the probe inside; flushes effects. */
async function render(defaultLinked = false) {
  await act(async () => {
    root.render(
      // `children` is a REQUIRED prop of PageSnapshotProviderProps, so the
      // positional form the rule asks for does not typecheck.
      // eslint-disable-next-line react/no-children-prop
      createElement(PageSnapshotProvider, {
        defaultLinked,
        children: createElement(Probe),
      }),
    );
  });
}

/**
 * Render in CONTROLLED mode — the host owns `linked` and receives writes.
 * This is the seam that replaced the provider's direct `useChatSettings`
 * import (the one cycle in the package graph): persistence now belongs to
 * whoever owns the setting, so it must be provable from outside.
 */
async function renderControlled(initial: boolean) {
  const writes: boolean[] = [];
  let current = initial;
  const paint = async () => {
    await act(async () => {
      root.render(
        // `children` is a REQUIRED prop of PageSnapshotProviderProps, so the
        // positional form the rule asks for does not typecheck.
        // eslint-disable-next-line react/no-children-prop
        createElement(PageSnapshotProvider, {
          linked: current,
          onLinkedChange: (next: boolean) => {
            writes.push(next);
            current = next;
          },
          children: createElement(Probe),
        }),
      );
    });
  };
  await paint();
  return { writes, repaint: paint, get value() { return current; } };
}

describe('PageSnapshotProvider — controlled opt-in', () => {
  it('renders the host-owned value rather than its own state', async () => {
    await renderControlled(true);
    expect(ctx!.isLinked).toBe(true);
  });

  it('routes a toggle to the host instead of self-updating', async () => {
    const host = await renderControlled(false);

    await act(async () => ctx!.setIsLinked(true));

    // The host saw the write...
    expect(host.writes).toEqual([true]);
    // ...and until the host re-renders with the new value, the provider must
    // NOT have quietly kept its own copy — that would fork the two.
    expect(ctx!.isLinked).toBe(false);

    await host.repaint();
    expect(ctx!.isLinked).toBe(true);
  });
});

describe('PageSnapshotProvider / usePageSnapshot', () => {
  it('defaults to not linked', async () => {
    await render();
    expect(ctx!.isLinked).toBe(false);
    expect(ctx!.lastSnapshot).toBeNull();
  });

  it('capture() returns null while not linked', async () => {
    await render();
    let result: unknown;
    act(() => {
      result = ctx!.capture();
    });
    expect(result).toBeNull();
  });

  it('getChatMetadata() returns undefined while not linked', async () => {
    await render();
    expect(ctx!.getChatMetadata()).toBeUndefined();
  });

  it('generatePreview() works even when not linked (preview gate)', async () => {
    document.body.innerHTML += '<main><h1>Preview Page</h1></main>';
    await render();
    let preview: ReturnType<PageSnapshotContextValue['generatePreview']>;
    act(() => {
      preview = ctx!.generatePreview();
    });
    expect(preview!).not.toBeNull();
    expect(preview!.payload.snapshot.type).toBe('root');
  });

  it('opting in captures an initial snapshot', async () => {
    document.body.innerHTML += '<main><h1>Linked Page</h1></main>';
    await render();
    await act(async () => {
      ctx!.setIsLinked(true);
    });
    expect(ctx!.isLinked).toBe(true);
    expect(ctx!.lastSnapshot).not.toBeNull();
  });

  it('getChatMetadata() returns { pageContext } when linked', async () => {
    document.body.innerHTML += '<main><h1>Meta Page</h1></main>';
    await render(true);
    let meta: Record<string, unknown> | undefined;
    await act(async () => {
      meta = ctx!.getChatMetadata();
    });
    expect(meta).toBeDefined();
    expect(meta).toHaveProperty('pageContext');
  });

  /**
   * Staleness is what tells the user the assistant is answering about a page
   * that has since moved. It shipped inert — `setIsStale(true)` existed
   * nowhere — so the chip could never warn and the hash, its four tests and
   * `contentHash` had no consumer.
   *
   * Both directions are asserted: a mechanism only ever observed saying "no"
   * has not been observed working.
   */
  describe('staleness', () => {
    /**
     * These tests REPLACE the body rather than appending to it. The suite's
     * `afterEach` unmounts the root but leaves the document, and the other
     * tests append with `+=`, so by the time this block runs the page holds
     * several `<main>` elements — and scope Tier 2 picks the largest by area,
     * not the one this test just wrote. Staleness compares two captures, so a
     * capture of the wrong root reports "unchanged" while the element under
     * test did change.
     */
    beforeEach(() => {
      document.body.innerHTML = '';
    });

    it('is false before anything has been sent — there is no claim to be stale against', async () => {
      document.body.innerHTML = '<main><h1>Fresh</h1></main>';
      await render(true);
      await act(async () => {
        ctx!.refresh();
      });
      expect(ctx!.isStale).toBe(false);
    });

    it('turns true when the page changes after a send', async () => {
      document.body.innerHTML = '<main id="scope"><h1>Before</h1></main>';
      await render(true);
      await act(async () => {
        ctx!.getChatMetadata();
      });
      expect(ctx!.isStale).toBe(false);

      document.querySelector('#scope')!.innerHTML = '<h1>After</h1><p>New</p>';
      await act(async () => {
        ctx!.refresh();
      });
      expect(ctx!.isStale).toBe(true);
    });

    it('stays false when the page is re-captured unchanged', async () => {
      document.body.innerHTML = '<main><h1>Same</h1></main>';
      await render(true);
      await act(async () => {
        ctx!.getChatMetadata();
      });
      await act(async () => {
        ctx!.refresh();
      });
      expect(ctx!.isStale).toBe(false);
    });

    it('clears when a fresh snapshot is sent', async () => {
      document.body.innerHTML = '<main id="scope"><h1>One</h1></main>';
      await render(true);
      await act(async () => {
        ctx!.getChatMetadata();
      });
      document.querySelector('#scope')!.innerHTML = '<h1>Two</h1>';
      await act(async () => {
        ctx!.refresh();
      });
      expect(ctx!.isStale).toBe(true);

      await act(async () => {
        ctx!.getChatMetadata();
      });
      expect(ctx!.isStale).toBe(false);
    });
  });
});
