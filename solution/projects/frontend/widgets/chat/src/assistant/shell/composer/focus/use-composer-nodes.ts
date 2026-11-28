import { useCallback, type RefObject } from 'react';

/**
 * The composer's own elements, found from a marker rendered inside it. The widget keeps the field and the microphone private, so the DOM is the only route; the
 * selectors are the widget's classes (`composer-box`, `composer-mic`), which its stylesheet also relies on.
 */
export function useComposerNodes(marker: RefObject<HTMLElement | null>) {
  const box = useCallback(() => marker.current?.closest('.composer-box') ?? null, [marker]);
  const mic = useCallback(() => box()?.querySelector<HTMLButtonElement>('.composer-mic') ?? null, [box]);
  const field = useCallback(() => box()?.querySelector<HTMLTextAreaElement>('textarea') ?? null, [box]);
  return { mic, field };
}

export type ComposerNodes = ReturnType<typeof useComposerNodes>;
