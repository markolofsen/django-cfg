import { useEffect } from 'react';

import type { ComposerNodes } from './use-composer-nodes';

/**
 * While `active`, the field may only grow. Dictation arrives in bursts and the engine revises its guess, so the height would otherwise go up and down with each one:
 * the tallest height seen is kept as a floor, and the floor goes when `active` ends.
 */
export function useHeightFloor({ field }: ComposerNodes, active: boolean): void {
  useEffect(() => {
    const node = field();
    if (!active || !node) return;
    let tallest = 0;
    const watch = new ResizeObserver(() => {
      const height = node.offsetHeight;
      if (height > tallest) {
        tallest = height;
        node.style.minHeight = `${height}px`;
      }
    });
    watch.observe(node);
    return () => {
      watch.disconnect();
      node.style.minHeight = '';
    };
  }, [active, field]);
}
