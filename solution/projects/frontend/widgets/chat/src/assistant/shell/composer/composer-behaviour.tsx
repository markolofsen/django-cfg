'use client';

import { useCallback, useEffect, useRef } from 'react';

import { useHotkey } from '@djangocfg/ui-core/hooks';
import { useComposer } from '../../../chat/composer';
import { useTurn } from '../../../chat/store';

import { useCaretFocus } from './focus/use-caret-focus';
import { clearPendingPrompt, usePendingPrompt } from './handoff';
import { useComposerNodes } from './focus/use-composer-nodes';
import { DICTATION_TOGGLE } from './keys';
import { useFocusArea } from './focus/use-focus-area';
import { useGracefulStop } from './dictation/use-graceful-stop';
import { useHeightFloor } from './focus/use-height-floor';
import { useRecording } from './dictation/use-recording';

interface Props {
  focusWhen?: boolean;
  refocus?: boolean;
}

/**
 * What the widget's composer lacks, mounted inside it (the `toolbarEnd` slot, the only place the draft's `send` is reachable). Renders nothing.
 *
 * While dictation is on, Enter and Escape mean the same wherever the focus is: pressing the microphone leaves the focus on that button, so Enter re-pressed it and
 * merely stopped the recording, and the field's own Enter handling works only with the caret in the field. Enter stops the recording and sends what was heard;
 * Escape stops it and keeps the text. The field's height and the caret are handled by the hooks beside this file.
 */
export function ComposerBehaviour({ focusWhen = false, refocus = false }: Props) {
  const marker = useRef<HTMLSpanElement>(null);
  const nodes = useComposerNodes(marker);
  const { field } = nodes;
  const composer = useComposer();
  const latest = useRef(composer);
  latest.current = composer;

  // A prompt asked from outside the assistant (`askAssistant`): into the draft, then sent once the draft holds it and sending is allowed.
  const pendingPrompt = usePendingPrompt();
  const draftText = composer.draft.text;
  const canSend = composer.canSend;
  useEffect(() => {
    if (!pendingPrompt) return;
    if (draftText !== pendingPrompt) {
      latest.current.setText(pendingPrompt);
      return;
    }
    if (canSend) {
      clearPendingPrompt();
      latest.current.send();
    }
  }, [pendingPrompt, draftText, canSend]);

  const recording = useRecording(nodes);
  useHeightFloor(nodes, recording);
  useFocusArea(nodes, marker, refocus);
  const { isStreaming } = useTurn();
  useCaretFocus(nodes, { focusWhen, refocus, recording, streaming: isStreaming, onSend: composer.onSend });

  // Waits for the words still being recognised, then commits them into the draft; sending reads the draft after that.
  const stop = useGracefulStop(nodes, recording, useCallback(() => latest.current.draft.text, []));

  const sendWhenStopped = useCallback(() => {
    stop(() => {
      if (latest.current.canSend) latest.current.send();
    });
  }, [stop]);

  // In the field the widget's own Enter would send at once and cut the dictation; this capture listener takes the key first, so the send waits like the stop does.
  useEffect(() => {
    const node = field();
    if (!recording || !node) return;
    const take = (event: KeyboardEvent) => {
      if (event.key !== 'Enter' || event.shiftKey || event.altKey || event.ctrlKey || event.metaKey || event.isComposing) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      sendWhenStopped();
    };
    node.addEventListener('keydown', take, true);
    return () => node.removeEventListener('keydown', take, true);
  }, [recording, field, sendWhenStopped]);

  // Elsewhere (the focus stayed on the microphone button) the same Enter comes through the hotkey.
  useHotkey(
    'enter',
    (event) => {
      if (event.target instanceof HTMLTextAreaElement) return;
      sendWhenStopped();
    },
    { enabled: recording, inInput: true, preventDefault: true },
  );
  // One key to start and to stop, wherever the focus is. Stopping waits like every other stop; starting is the microphone's own press.
  useHotkey(DICTATION_TOGGLE, () => (recording ? stop() : nodes.mic()?.click()), { inInput: true, preventDefault: true });
  useHotkey('escape', () => stop(), { enabled: recording, inInput: true, preventDefault: true });

  // Assistive technology and password managers learn the key from the button itself.
  const { mic } = nodes;
  useEffect(() => {
    mic()?.setAttribute('aria-keyshortcuts', 'Meta+D Control+D');
  }, [mic, recording]);

  return <span ref={marker} hidden />;
}
