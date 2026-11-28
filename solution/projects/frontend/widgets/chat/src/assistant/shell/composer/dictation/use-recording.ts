import { useEffect, useState } from 'react';

import type { ComposerNodes } from '../focus/use-composer-nodes';

/** Whether dictation is on. The widget does not expose it, so it is read from the microphone's `data-recording` attribute (the one its halo is styled from). */
export function useRecording({ mic }: ComposerNodes): boolean {
  const [recording, setRecording] = useState(false);
  useEffect(() => {
    const button = mic();
    if (!button) return;
    const read = () => setRecording(button.hasAttribute('data-recording'));
    read();
    const watch = new MutationObserver(read);
    watch.observe(button, { attributes: true, attributeFilter: ['data-recording'] });
    return () => watch.disconnect();
  }, [mic]);
  return recording;
}
