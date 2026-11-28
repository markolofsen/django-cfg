'use client';

import type * as React from 'react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { AlertCircle, Loader2, Mic } from 'lucide-react';

import { useNotificationSounds } from '@djangocfg/ui-core/hooks';
import { cn } from '@djangocfg/ui-core/lib';
import { TooltipHint } from '@djangocfg/ui-core/components';
// The registry is the slot bridge: it carries both the composer handle and
// the size context, so a slot widget never imports from the chat package.
import {
  subscribeComposerSubmit,
  useActiveComposer,
  useResolvedComposerSize,
} from '../../composer-registry';
import { useResolvedLanguage } from '../hooks/useResolvedLanguage';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { useVoiceSupport } from '../hooks/useVoiceSupport';
import { getSpeechLogger } from '../core/logger';
import { DEFAULT_VOICE_SOUNDS, type VoiceSoundEvent } from '../core/audio/defaults';
import { LanguageChip } from '../components/LanguageChip';
import { VoiceBars } from '../components/VoiceBars';
import { useSpeechPrefs } from '../store/prefsStore';
import { VoiceControlMenu } from './VoiceControlMenu';
import type { RecognitionEngine } from '../types';

/** High-level visual state the composer mic button reflects. */
export type VoiceSlotState = 'idle' | 'listening' | 'processing' | 'error';

const log = getSpeechLogger();

export interface VoiceComposerSlotProps {
  /**
   * Controlled composer value. Optional — when omitted, the slot
   * reads/writes through the Chat context's registered `ComposerHandle`
   * (built-in `<Composer>` and any host that calls
   * `useRegisterComposer({ getValue, setValue })`). Pass explicitly
   * only for standalone usage outside a `<ChatProvider>`.
   */
  value?: string;
  /** Composer setter — see `value`. Optional when used inside a chat. */
  onChange?: (next: string) => void;
  /** Optional custom engine (Deepgram / HTTP / WS). Defaults to Web Speech. */
  engine?: RecognitionEngine;
  /** BCP-47 language override. Otherwise `useSpeechPrefs` decides. */
  language?: string;
  /** Hide the button if the host wants to disable voice on phones. */
  hideOnMobile?: boolean;
  /** Max session length in seconds before we auto-stop. Default 90. */
  maxSeconds?: number;
  /** Auto-stop after this many ms of silence. Default 2500. */
  silenceMs?: number;
  /**
   * Button size. Omit to inherit the surrounding composer's size (via
   * the composer size context) so the mic, ✕/✓ and Send always match;
   * standalone use falls back to 'md'.
   */
  size?: 'sm' | 'md' | 'lg';
  /** Override classes on the button. */
  className?: string;
  /** Fires when dictation finishes — useful for parent-side analytics. */
  onFinish?: (transcript: string) => void;
  /**
   * Start/stop earcons. `true` (default) plays the bundled sounds,
   * `false` disables them, or pass `{ start, stop }` data-URLs to
   * override. Master mute lives in `useNotificationSounds` localStorage
   * — users can silence everything via their own UI.
   */
  sounds?: boolean | { start?: string; stop?: string };
  /** Notified whenever the high-level visual state changes. */
  onStateChange?: (state: VoiceSlotState) => void;
  /**
   * Render the chevron `<VoiceControlMenu>` (device + language +
   * hold-to-record) next to the mic. @default true
   */
  showMenu?: boolean;
  /**
   * Narrow the language lists (menu + in-recording chip) to a subset
   * of BCP-47 tags. `[]` hides both — use for server engines that
   * detect language themselves.
   */
  allowedTags?: string[];
}

/**
 * Per-size geometry. Mirrors the chat composer action-bar buttons
 * (`composer-kit/ComposerButton` `BUTTON_SIZE`) so the slot drops into
 * `composerSlots.inlineEnd` round and correctly sized with no host CSS.
 */
const SIZE_CLS: Record<NonNullable<VoiceComposerSlotProps['size']>, string> = {
  sm: 'h-7 w-7 rounded-md [&_svg]:size-4',
  md: 'h-9 w-9 rounded-lg [&_svg]:size-[1.125rem]',
  lg: 'h-11 w-11 rounded-lg [&_svg]:size-5',
};

const STORAGE_KEY = 'djangocfg-stt:voice-sounds';

/**
 * Drop-in microphone slot for `<Composer>` — pass it as a raw node via
 * `composerSlots.inlineEnd` (inline layout) or `composerSlots.blockStart`.
 *
 * Renders a microphone button — but only when the browser + device
 * combination can actually do speech recognition. Firefox, in-app
 * WebViews, and missing `getUserMedia` all collapse the component to
 * `null`, so the chat composer never shows a broken affordance.
 *
 * While listening, interim+final transcript is pushed live into the
 * composer's `value` — like dictation on iOS / Android keyboards. The
 * user's already-typed prefix is preserved (anchored on press). Cancel
 * with the same button or by pressing Escape (handled upstream).
 *
 * Soft start/stop earcons play by default. Pass `sounds={false}` to
 * mute, or `sounds={{ start, stop }}` to override the audio URLs.
 */
export function VoiceComposerSlot({
  value,
  onChange,
  engine,
  language,
  hideOnMobile = false,
  maxSeconds = 90,
  silenceMs = 2500,
  size,
  className,
  onFinish,
  sounds = true,
  onStateChange,
  showMenu = true,
  allowedTags,
}: VoiceComposerSlotProps): React.ReactElement | null {
  const support = useVoiceSupport(engine);
  // One control height for the whole action bar — inherited from the
  // composer unless the host pins it (mismatched mic vs Send heights
  // were the first thing the owner saw, 2026-08-03).
  const resolvedSize = useResolvedComposerSize(size);

  // Read the active composer handle from the cross-tool registry
  // (`@djangocfg/widget-forms/composer-registry`). The built-in
  // `<Composer>` (and TipTap hosts via `useRegisterComposer`) publish
  // their handle to this registry on mount. Falls back to a no-op
  // when nothing is registered (no composer in the tree).
  const activeComposer = useActiveComposer();
  const composerHandleRef = useRef(activeComposer);
  composerHandleRef.current = activeComposer;

  useEffect(() => {
    log.slot.debug('mount', {
      supported: support.supported,
      reason: support.reason,
      hasComposerHandle: !!activeComposer,
      hasExplicitValue: value !== undefined,
      hasOnChange: !!onChange,
    });
  }, [support.supported, support.reason, activeComposer, value, onChange]);

  // Resolve value/onChange: prop wins; otherwise pull from the
  // registered composer handle. The slot can therefore be dropped into
  // `composerBlockStart` of `ChatRoot` with zero props.
  const resolvedGetValue = useCallback((): string => {
    if (value !== undefined) return value;
    return composerHandleRef.current?.getValue?.() ?? '';
  }, [value]);
  const resolvedSetValue = useCallback(
    (next: string): void => {
      if (onChange) {
        log.composer.debug('setValue → onChange prop', { len: next.length });
        onChange(next);
        return;
      }
      const handle = composerHandleRef.current;
      if (!handle?.setValue) {
        log.composer.warn(
          'setValue called but no composer handle is registered — text will be lost. ' +
            'Make sure <VoiceComposerSlot> lives inside a <ChatProvider> (or pass `value`/`onChange` props for standalone use).',
          { len: next.length },
        );
        return;
      }
      log.composer.debug('setValue → composer handle', { len: next.length });
      handle.setValue(next);
    },
    [onChange],
  );

  // Anchor: what was already in the textarea when the user pressed the
  // mic. Live transcript is appended to this baseline so manual typing
  // before pressing the button is never overwritten.
  const anchorRef = useRef<string>('');
  const onFinishRef = useRef(onFinish);
  onFinishRef.current = onFinish;

  // Push caret to the end on the next frame — after React commits the
  // new `value` into the DOM. Without the rAF the selection lands on
  // the old text length, leaving the cursor mid-string while the live
  // transcript visually keeps growing.
  const pinCaretToEnd = useCallback(() => {
    const handle = composerHandleRef.current;
    if (!handle?.moveCursorToEnd) return;
    requestAnimationFrame(() => {
      composerHandleRef.current?.moveCursorToEnd?.();
    });
  }, []);

  // Earcon bus. `sounds === false` → pass empty map so the bus stays
  // silent. Object overrides merge with bundled defaults.
  const soundMap =
    sounds === false
      ? undefined
      : sounds === true
        ? DEFAULT_VOICE_SOUNDS
        : { ...DEFAULT_VOICE_SOUNDS, ...sounds };
  const audio = useNotificationSounds<VoiceSoundEvent>({
    storageKey: STORAGE_KEY,
    sounds: soundMap,
    muted: sounds === false,
    // Both earcons stay deliberately quiet — they're self-initiated
    // micro-confirmations, not notifications. Anything louder feels
    // attention-grabbing when the user pressed the button themselves.
    eventVolumes: { start: 0.35, stop: 0.5 },
  });

  // Restart marker: language switched mid-session, so the engine must
  // be fully torn down and started again. The restart happens in
  // `onStop` — i.e. AFTER the engine reports 'closed'. Starting any
  // earlier races the async teardown (Web Speech fires `onend` well
  // after `abort()`), and the engine silently ignores the start.
  const restartAfterAbortRef = useRef(false);
  const recRef = useRef<{ start: () => Promise<void> } | null>(null);

  const rec = useSpeechRecognition({
    engine,
    language,
    interim: true,
    autoStop: { silenceMs, maxMs: maxSeconds * 1000 },
    onStart: () => {
      void audio.play('start');
      // Focus the composer + park caret at the end so the live
      // transcript visibly grows where the user expects it to.
      composerHandleRef.current?.focus();
      pinCaretToEnd();
    },
    onStop: () => {
      if (restartAfterAbortRef.current) {
        // Language-switch restart — the session continues, so no stop
        // earcon and no onFinish. Transcript state survives (only
        // RESET clears it), so nothing dictated is lost.
        //
        // Deferred a tick: engines that emit 'closed' synchronously
        // from abort() (external/mock) would otherwise hit start()'s
        // still-'listening' closure from the pre-abort render and be
        // silently ignored. After the tick React has committed the
        // stop, and recRef holds a start() that actually runs.
        restartAfterAbortRef.current = false;
        window.setTimeout(() => {
          void recRef.current?.start();
        }, 0);
        return;
      }
      void audio.play('stop');
      // Re-focus on stop too — auto-stop on silence happens without
      // a user gesture, and we want the user to keep typing seamlessly.
      composerHandleRef.current?.focus();
      pinCaretToEnd();
      onFinishRef.current?.(resolvedGetValue());
    },
  });
  recRef.current = rec;

  const prefs = useSpeechPrefs();

  // THE COMPOSER MIRRORS THE WHOLE SESSION TRANSCRIPT, not incremental
  // partial events. Chrome splits one utterance into several results;
  // rendering only the latest partial made the composer show just the
  // last word or two (owner report 2026-08-03). `rec.transcript`
  // accumulates every final segment + the trailing interim, so joining
  // it wholesale always paints the full sentence.
  const sessionText = [rec.transcript.final, rec.transcript.interim]
    .map((s) => s.trim())
    .filter(Boolean)
    .join(' ');
  useEffect(() => {
    if (!sessionText) return;
    const merged = anchorRef.current
      ? `${anchorRef.current} ${sessionText}`
      : sessionText;
    log.dictation.debug('transcript sync', { len: merged.length });
    resolvedSetValue(merged);
    pinCaretToEnd();
  }, [sessionText, pinCaretToEnd, resolvedSetValue]);

  // Web Speech pins `lang` per session — switching the language chip
  // mid-recording must therefore RESTART the session (see
  // restartAfterAbortRef above for why the start waits for 'closed').
  const resolvedLanguage = useResolvedLanguage(language);
  const prevLanguageRef = useRef(resolvedLanguage);
  const isListeningNow =
    rec.status === 'listening' || rec.status === 'starting';
  useEffect(() => {
    if (prevLanguageRef.current === resolvedLanguage) return;
    prevLanguageRef.current = resolvedLanguage;
    if (!isListeningNow) return;
    restartAfterAbortRef.current = true;
    rec.abort();
  }, [resolvedLanguage, isListeningNow, rec]);

  // Submitting the composer ends the session outright: the message is
  // leaving, so stop capturing — abort without rollback and clear the
  // transcript so the sync effect can't repaint dictated text into the
  // now-empty draft. (Owner ask 2026-08-03: Send must drop recording.)
  useEffect(() => {
    return subscribeComposerSubmit(() => {
      if (rec.status !== 'listening' && rec.status !== 'starting') return;
      restartAfterAbortRef.current = false;
      anchorRef.current = '';
      rec.abort();
      rec.reset();
    });
  }, [rec]);

  // A `language-not-supported` engine error means the CHOICE is wrong,
  // not the mic — pop the language menu open instead of a dead chip.
  const [chipOpen, setChipOpen] = useState(false);
  useEffect(() => {
    if (rec.error?.code === 'language') setChipOpen(true);
  }, [rec.error]);

  // Hotkeys while listening:
  //   Esc   — cancel dictation (and stop event propagation so the
  //           outer chat doesn't *also* close — same convention as
  //           ChatGPT / Slack voice mode).
  //   Enter — finish dictation, KEEP what we already pushed into the
  //           composer, do NOT submit the chat (avoids accidental
  //           sends while the user is still talking). We block the
  //           Enter that would otherwise reach the composer textarea
  //           by listening in the capture phase.
  // Cancel = discard: abort the engine AND roll the composer back to
  // the pre-dictation anchor. Partials/finals already pushed into the
  // textarea must not survive an explicit cancel (claude.ai's ✕).
  const cancelDictation = useCallback(() => {
    rec.abort();
    // Clear the session transcript FIRST — otherwise the transcript
    // sync effect would immediately re-paint the discarded text.
    rec.reset();
    resolvedSetValue(anchorRef.current);
    pinCaretToEnd();
  }, [pinCaretToEnd, rec, resolvedSetValue]);

  const listening = rec.status === 'listening' || rec.status === 'starting';
  useEffect(() => {
    if (!listening) return undefined;
    const onKey = (e: KeyboardEvent): void => {
      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        cancelDictation();
        return;
      }
      if (e.key === 'Enter' && !e.shiftKey) {
        // Block the chat composer's "Enter to send" while we're
        // dictating — finish recording instead.
        e.preventDefault();
        e.stopPropagation();
        void rec.stop();
      }
    };
    // `capture: true` so we run before the composer textarea's
    // keydown handler (which would otherwise close the chat on Esc
    // or submit the form on Enter).
    window.addEventListener('keydown', onKey, true);
    return () => {
      window.removeEventListener('keydown', onKey, true);
    };
  }, [listening, rec, cancelDictation]);

  const beginDictation = useCallback(() => {
    anchorRef.current = resolvedGetValue().trim();
    // Fresh session — drop the previous session's transcript so the
    // sync effect starts from a clean slate.
    rec.reset();
    void rec.start();
  }, [rec, resolvedGetValue]);

  const toggle = useCallback(() => {
    if (rec.status === 'listening' || rec.status === 'starting') {
      void rec.stop();
      return;
    }
    // A tap while `stopping` (spinner) or `error` must ALWAYS recover the
    // control, not queue a start the engine silently drops. Force the
    // engine down and reset to idle first; the user can tap once more to
    // begin a fresh session. Without this the button reads as frozen —
    // the exact reported "can't even stop it" behaviour.
    if (rec.status === 'stopping' || rec.status === 'error') {
      rec.abort();
      rec.reset();
      return;
    }
    beginDictation();
  }, [rec, beginDictation]);

  // Hold-to-record (prefs-gated): press starts, release finishes —
  // claude.ai's "Hold to record" switch. Pointer capture would eat the
  // Tooltip; plain down/up + leave-guard is enough.
  const holdMode = prefs.holdToRecord;
  const handleHoldDown = useCallback(
    (e: React.PointerEvent) => {
      e.preventDefault();
      // Stuck in the spinner or an error from a prior hold? Recover
      // instead of trying to start a session the engine would ignore —
      // this press clears it; the next hold records. (Mirrors `toggle`.)
      if (rec.status === 'stopping' || rec.status === 'error') {
        rec.abort();
        rec.reset();
        return;
      }
      if (!listening) beginDictation();
    },
    [listening, beginDictation, rec],
  );
  const handleHoldRelease = useCallback(() => {
    if (listening) void rec.stop();
  }, [listening, rec]);

  // Derive the high-level visual state from the engine status. The
  // engine owns the truth — `processing` is the post-speech tail while
  // the final result settles (`stopping`), `error` is a recoverable
  // failure that resets to `idle` on the next press.
  const stopping = rec.status === 'stopping';
  const slotState: VoiceSlotState = listening
    ? 'listening'
    : stopping
      ? 'processing'
      : rec.status === 'error'
        ? 'error'
        : 'idle';

  // Notify the host on every transition (after render, ref-guarded so
  // identical states never fire twice).
  const lastStateRef = useRef<VoiceSlotState | null>(null);
  const onStateChangeRef = useRef(onStateChange);
  onStateChangeRef.current = onStateChange;
  useEffect(() => {
    if (lastStateRef.current === slotState) return;
    lastStateRef.current = slotState;
    onStateChangeRef.current?.(slotState);
  }, [slotState]);

  if (!support.supported) return null;
  if (hideOnMobile && support.isMobile) return null;

  // Tooltip: countdown + hotkey hint while listening, error copy on
  // failure, plain prompt otherwise.
  const tooltip =
    slotState === 'listening'
      ? 'Stop dictation · Esc to cancel'
      : slotState === 'processing'
        ? 'Transcribing…'
        : slotState === 'error'
          ? rec.error?.message || 'Dictation failed — tap to retry'
          : holdMode
            ? 'Hold to record'
            : 'Dictate message';

  const ariaLabel =
    slotState === 'listening'
      ? 'Stop dictation'
      : slotState === 'error'
        ? 'Dictation failed — retry'
        : 'Dictate message';

  // Language surfaces hide when the host hard-pins `language` (the
  // chip could not change anything) or opts out via `allowedTags: []`
  // (server engines that detect language themselves).
  const showLanguageChip =
    language === undefined && (allowedTags === undefined || allowedTags.length > 0);

  const micButtonHandlers = holdMode
    ? {
        onPointerDown: handleHoldDown,
        onPointerUp: handleHoldRelease,
        onPointerLeave: handleHoldRelease,
      }
    : { onClick: toggle };

  // ONE pattern, zero explanation needed (owner call 2026-08-03, third
  // iteration): the mic NEVER moves. While recording it turns red and
  // PULSES with the voice — click it to stop, exactly like ChatGPT /
  // Telegram. No ✓ (it competed with Send), no spinner, no wave, no ✕
  // (owner: not needed — Esc cancels). The only listening-time
  // addition is the tiny language chip left of the mic.
  const listeningNow = slotState === 'listening';
  return (
    <span className="inline-flex items-center gap-1 !h-auto">
      {listeningNow && showLanguageChip ? (
        <LanguageChip
          allowedTags={allowedTags}
          open={chipOpen}
          onOpenChange={setChipOpen}
        />
      ) : null}
      {/* A wrong-language pick is recoverable in place — reopen the
          chip's menu instead of showing a dead "Failed" badge. */}
      {slotState === 'error' && rec.error?.code === 'language' && showLanguageChip ? (
        <LanguageChip
          allowedTags={allowedTags}
          open={chipOpen}
          onOpenChange={setChipOpen}
        />
      ) : null}
      {/* The chevron companion menu — devices, live mic check, language,
          hold-to-record. LEFT of the mic; hidden while recording. */}
      {showMenu && !listeningNow ? (
        <VoiceControlMenu allowedTags={allowedTags} />
      ) : null}
      <TooltipHint tooltip={{ content: tooltip, side: 'top' }}>
        <button
          type="button"
          {...micButtonHandlers}
          aria-pressed={listeningNow}
          aria-label={ariaLabel}
          data-state={slotState}
          className={cn(
            // Shape comes from SIZE_CLS — mirrors ComposerButton's
            // Claude-style soft-radius squares.
            'relative inline-flex items-center justify-center transition-all duration-200',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
            SIZE_CLS[resolvedSize],
            listeningNow &&
              'bg-destructive text-destructive-foreground hover:bg-destructive/90',
            slotState === 'processing' &&
              'bg-primary/10 text-primary hover:bg-primary/15',
            slotState === 'error' &&
              'bg-destructive/10 text-destructive hover:bg-destructive/15',
            slotState === 'idle' &&
              'text-muted-foreground hover:bg-muted hover:text-foreground',
            className,
          )}
        >
          {listeningNow ? (
            // The dictaphone-app equalizer replaces the mic glyph
            // while recording — bars dance with the live level.
            <VoiceBars level={rec.level} />
          ) : slotState === 'processing' ? (
            <Loader2 className="animate-spin" />
          ) : slotState === 'error' ? (
            <AlertCircle />
          ) : (
            <Mic className="transition-transform duration-200" />
          )}
        </button>
      </TooltipHint>
    </span>
  );
}
