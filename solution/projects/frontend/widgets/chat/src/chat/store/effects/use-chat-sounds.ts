import { useEffect, useRef } from "react";

import { createSoundBus } from "@djangocfg/ui-core/hooks";

import type { ChatSoundsCapability, ChatSoundEvent } from "../../core/capabilities";
import type { ChatStore } from "../store";
import * as bundled from "../../sounds";

/** Quieter than a notification: a message sound is a confirmation, not an alert. Per event, on top of the capability's volume. */
const EVENT_VOLUME: Readonly<Record<ChatSoundEvent, number>> = { messageSent: 0.5, messageReceived: 0.7, streamStart: 0.3, error: 0.25 };

const BUNDLED: Readonly<Record<ChatSoundEvent, string>> = {
  messageSent: bundled.sent,
  messageReceived: bundled.received,
  streamStart: bundled.start,
  error: bundled.error,
};

/**
 * Plays the chat's message sounds from what the store does: a prompt sent, the answer starting to stream, the answer finishing, a turn failing.
 * On by default; `sounds: false` silences it, `sounds.urls` replaces or (with `false`) mutes one event. Driven by transitions after the first render, so loading
 * a history, or switching to another conversation, plays nothing. Needs a prior user gesture (the browser's rule); the bus unlocks on the first click or key.
 */
export function useChatSounds(store: ChatStore, config: ChatSoundsCapability | false | undefined): void {
  const latest = useRef(config);
  latest.current = config;
  const off = config === false;

  useEffect(() => {
    if (off) return;
    const bus = createSoundBus<ChatSoundEvent>({
      sounds: BUNDLED,
      getVolume: (event) => (latest.current === false ? 0 : (latest.current?.volume ?? 1)) * (event ? EVENT_VOLUME[event] : 1),
      getMuted: () => latest.current === false || latest.current?.muted === true,
      isEnabled: () => true,
    });
    const apply = () => {
      const urls = latest.current === false ? undefined : latest.current?.urls;
      bus.setSounds({ ...BUNDLED, ...urls });
    };
    apply();
    let before = store.getState();
    const unsubscribe = store.subscribe(() => {
      const now = store.getState();
      const was = before;
      before = now;
      if (!was.historyLoaded || !now.historyLoaded) return;
      apply();
      const a = was.transcript;
      const b = now.transcript;
      const grown = b.ids.length > a.ids.length && a.ids.every((id, index) => b.ids[index] === id);
      if (grown && b.ids.slice(a.ids.length).some((id) => b.byId[id]?.role === "user" && b.byId[id]?.from !== "other")) bus.play("messageSent");
      if (a.streamingId === null && b.streamingId !== null) bus.play("streamStart");
      // A message that was streaming and is now settled: finished, or failed.
      for (const id of a.ids) {
        const prev = a.byId[id]?.status.state;
        const next = b.byId[id]?.status.state;
        if (prev !== "streaming" || next === undefined || next === "streaming") continue;
        if (next === "complete") bus.play("messageReceived");
        else if (next === "failed") bus.play("error");
      }
    });
    return () => {
      unsubscribe();
      bus.dispose();
    };
  }, [store, off]);
}
