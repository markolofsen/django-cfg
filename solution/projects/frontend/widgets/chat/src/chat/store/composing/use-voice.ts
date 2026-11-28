import { useEffect, useMemo, useRef, useState } from "react";

import {
  VoiceSession,
  createWebSpeechCapability,
  type PlayEarcon,
  type VoiceCapability,
  type VoiceSnapshot,
} from "../../core";

/**
 * React binding for `VoiceSession`.
 *
 * Deliberately thin, exactly like `useMentions`. Everything with a race in it —
 * a result arriving after stop, an engine that ends on its own, the interim that
 * must replace rather than append — lives in `core/voice`, tested without a DOM.
 * This file only subscribes.
 */

export interface UseVoiceResult extends VoiceSnapshot {
  /** Whether a microphone exists at all. `false` ⇒ render no control. */
  readonly available: boolean;
  readonly start: () => void;
  readonly stop: () => void;
  readonly cancel: () => void;
  /** Take the dictated text and reset, for handing to the draft. */
  readonly take: () => string;
}

const IDLE: VoiceSnapshot = {
  recording: false,
  committed: "",
  interim: "",
  text: "",
};

export function useVoice(
  capability?: VoiceCapability | false,
  language = "en-US",
  playEarcon?: PlayEarcon,
): UseVoiceResult {
  const [snapshot, setSnapshot] = useState(IDLE);

  // Read through a ref for the same reason the capability is: a host passes an
  // inline arrow at every realistic call site, so keying the session on it would
  // rebuild the session mid-sentence and drop the words.
  const currentEarcon = useRef(playEarcon);
  currentEarcon.current = playEarcon;

  // The language, readable at START without being a dependency. The default
  // engine reads it through this function, so changing the language applies to
  // the NEXT dictation instead of rebuilding the session mid-sentence.
  const currentLanguage = useRef(language);
  currentLanguage.current = language;

  // The package's own engine, built at most once. `undefined` on a browser with
  // no Web Speech, which is what makes "no engine ⇒ no button" hold.
  const fallback = useMemo(
    () => createWebSpeechCapability({ language: () => currentLanguage.current }),
    [],
  );

  // Absent capability falls back to the browser rather than to nothing — the
  // one capability where absent does not mean absent. A host that supplies one
  // overrides the default outright, and `false` refuses the fallback too, which
  // is the only way to say "no dictation" when absence already means "default".
  const effective = capability === false ? undefined : (capability ?? fallback);

  // Same reason as `useMentions`: the capability is an object literal at every
  // realistic call site, so it is a new reference on every parent render.
  // Keying the session on it would rebuild it mid-sentence and drop the words.
  const latest = useRef(effective);
  latest.current = effective;

  const hasEngine = effective !== undefined;

  const session = useMemo(() => {
    if (effective === undefined) return null;
    return new VoiceSession({
      // Read through the ref so a re-created capability object still routes to
      // the host's CURRENT engine without rebuilding the session.
      capability: {
        start: (onText, signal) => latest.current!.start(onText, signal),
        stop: () => latest.current!.stop(),
      },
      onChange: setSnapshot,
      // Through the ref, so a host that rebuilds the callback each render still
      // reaches its CURRENT player without the session being rebuilt.
      playEarcon: (kind) => currentEarcon.current?.(kind),
    });
    // Presence alone rebuilds it. A `VoiceCapability` has no behavioural
    // primitives to key on — both members are functions, and functions are read
    // through the ref — so this is the whole dependency. Keyed on the EFFECTIVE
    // engine: a host capability arriving late must replace the default, and
    // keying on `capability` alone would leave the browser engine in place.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasEngine]);

  useEffect(() => () => session?.dispose(), [session]);

  // The ACTIONS memo on `session` alone, never on `snapshot` — the same defect
  // `use-mentions.ts` guards against. A caller may put `stop` in an effect's
  // dependency array (stopping dictation when a turn is sent is exactly that
  // shape); rebuilt on every snapshot, that effect would fire on each interim
  // result and re-run forever. Nothing about an action depends on the snapshot:
  // recording does not change what `cancel` does.
  const actions = useMemo(
    () => ({
      available: session !== null,
      start: () => session?.start(),
      stop: () => session?.stop(),
      cancel: () => session?.cancel(),
      take: () => session?.take() ?? "",
    }),
    [session],
  );

  return useMemo(() => ({ ...snapshot, ...actions }), [snapshot, actions]);
}
