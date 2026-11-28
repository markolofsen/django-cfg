import { useEffect } from 'react';

import type { ComposerNodes } from './use-composer-nodes';

const INTERACTIVE = 'button, a, input, textarea, select, [role="button"], [role="dialog"], [data-radix-popper-content-wrapper]';

/**
 * A press on the empty space around the composer (its column, and the padding of the chat under the transcript) puts the caret in the field, so the target is the whole
 * strip and not only the box. A press on a control, or anywhere in the transcript, is left alone. Keyboard devices only (`enabled`): on a phone it raises the keyboard.
 */
export function useFocusArea({ field }: ComposerNodes, marker: { current: HTMLElement | null }, enabled: boolean): void {
  useEffect(() => {
    const column = marker.current?.closest<HTMLElement>('.chat-column');
    const root = marker.current?.closest<HTMLElement>('.assistant-chat');
    if (!enabled || !column || !root) return;
    const take = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      // The root itself is its padding strip; inside it only the composer column counts, never the transcript.
      const inStrip = column.contains(target) || target === root;
      if (!inStrip || target.closest(INTERACTIVE)) return;
      event.preventDefault();
      const node = field();
      node?.focus();
      node?.setSelectionRange(node.value.length, node.value.length);
    };
    root.addEventListener('mousedown', take);
    return () => root.removeEventListener('mousedown', take);
  }, [enabled, field, marker]);
}
