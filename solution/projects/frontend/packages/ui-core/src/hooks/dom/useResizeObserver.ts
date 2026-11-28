// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Shared ResizeObserver store with refcounting.
//
// Why a shared observer (vs one per `useSize`/`useResizeObserver` call):
//   - A single ResizeObserver instance is cheaper than N when many
//     components subscribe (charts, sparklines, masonry items, …).
//   - Avoids "ResizeObserver loop completed with undelivered notifications"
//     warnings that pile up when many tiny observers fire in the same frame.
//
// The store keeps one global RO; per-element listener sets are reference
// counted so the observer detaches from elements once nobody listens.
//
// Inspired by the pattern at activity-graph.tsx:180-188 in jalcoui.

'use client';

import * as React from 'react';
import { useLayoutEffect } from './useLayoutEffect';

export interface Size {
  width: number;
  height: number;
}

type Listener = (size: Size) => void;

interface Entry {
  listeners: Set<Listener>;
  last: Size;
}

let sharedObserver: ResizeObserver | null = null;
const entries = new WeakMap<Element, Entry>();
// Mirror keyset so we can resolve elements from RO entries.
const elementByEntry = new WeakMap<Element, Entry>();

function getObserver(): ResizeObserver {
  if (sharedObserver) return sharedObserver;
  sharedObserver = new ResizeObserver((roEntries) => {
    for (const roEntry of roEntries) {
      const el = roEntry.target;
      const entry = elementByEntry.get(el);
      if (!entry) continue;

      let width: number;
      let height: number;
      const box = (roEntry as ResizeObserverEntry).borderBoxSize;
      if (box) {
        const b = Array.isArray(box) ? box[0] : box;
        width = b.inlineSize;
        height = b.blockSize;
      } else {
        width = (el as HTMLElement).offsetWidth;
        height = (el as HTMLElement).offsetHeight;
      }

      entry.last = { width, height };
      for (const listener of entry.listeners) listener(entry.last);
    }
  });
  return sharedObserver;
}

function subscribe(element: Element, listener: Listener): () => void {
  const observer = getObserver();
  let entry = entries.get(element);
  if (!entry) {
    entry = {
      listeners: new Set<Listener>(),
      last: {
        width: (element as HTMLElement).offsetWidth ?? 0,
        height: (element as HTMLElement).offsetHeight ?? 0,
      },
    };
    entries.set(element, entry);
    elementByEntry.set(element, entry);
    observer.observe(element);
  }
  entry.listeners.add(listener);
  // Deliver current size synchronously so consumers don't render with 0.
  listener(entry.last);

  return () => {
    const e = entries.get(element);
    if (!e) return;
    e.listeners.delete(listener);
    if (e.listeners.size === 0) {
      observer.unobserve(element);
      entries.delete(element);
    }
  };
}

/**
 * Observe an element's border-box size via a shared ResizeObserver.
 *
 * Returns `{ width: 0, height: 0 }` until the first measurement lands.
 * Pass either a ref or a callback-style ref result.
 *
 * @example
 * const ref = React.useRef<HTMLDivElement>(null);
 * const { width, height } = useResizeObserver(ref);
 */
export function useResizeObserver<T extends Element = Element>(
  ref: React.RefObject<T | null>,
): Size {
  const [size, setSize] = React.useState<Size>({ width: 0, height: 0 });

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    return subscribe(el, setSize);
  }, [ref]);

  return size;
}
