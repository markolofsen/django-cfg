import { useMemo, useRef, type ReactNode } from "react";

import type { ChatAdapter } from "../core/conversation/adapter";
import type { ChatCapabilities } from "../core/capabilities";
import { createChatEvents, type ChatEvents } from "../core/conversation/events";
import { ChatContext } from "./context";
import { useChatSounds } from "./effects/use-chat-sounds";
import { withModel } from "./send-request";
import { createChatStore, type ChatStore } from "./store";
import { ChatSurfacesContext, useSurfacesRegistry } from "./surfaces";

export interface ChatProviderProps {
  readonly adapter: ChatAdapter;
  readonly capabilities?: ChatCapabilities;
  /**
   * Bring your own store to seed history or drive it from outside. Omit and one
   * is created — the common path needs no lifecycle awareness at all.
   */
  readonly store?: ChatStore;
  readonly children: ReactNode;
}

const noCapabilities: ChatCapabilities = {};

/**
 * The escape hatch, and the seam every primitive resolves through.
 *
 * `<Chat>` renders this internally, so a host that outgrows the packaged layout
 * drops to primitives without losing state wiring — the thing that usually
 * forces a fork of the whole component.
 */
export function ChatProvider({
  adapter,
  capabilities = noCapabilities,
  store,
  children,
}: ChatProviderProps) {
  // The store is created ONCE and never re-created from a prop change.
  //
  // A `useMemo` keyed on [adapter, capabilities, store] reads as harmless and
  // is not: `capabilities` is an object literal at every realistic call site
  // (`<ChatProvider capabilities={{ think: … }}>`), so it is a new
  // reference on every parent render, and a new store means an EMPTY
  // transcript. The conversation would vanish mid-turn, with no error and
  // nothing in the stack pointing here.
  //
  // A ref, not a memo: `useMemo` is a performance hint React may discard and
  // recompute at will, so it is not a place to put something whose identity is
  // load-bearing. This is the documented distinction, not a style preference.
  //
  // `crypto.randomUUID` and `Date.now` are injected here, at the edge, so the
  // core stays clock-free and testable. This is the only place they appear.

  // The LIVE adapter, re-read on every send rather than captured once. A host
  // re-binds its adapter when the room changes (one transport per room), so a
  // store holding the first one addresses the room that was
  // open at mount: the start screen's first message landed in the previous
  // conversation instead of creating one. Re-creating the store for it is the
  // wrong fix — that is the defect the paragraph above guards against.
  const liveAdapter = useRef(adapter);
  liveAdapter.current = adapter;
  // Read at send time like the adapter: the model the switch shows when Send is pressed.
  const liveModel = useRef(capabilities.models?.value);
  liveModel.current = capabilities.models?.value;

  const ownStore = useRef<ChatStore | null>(null);
  if (ownStore.current === null && store === undefined) {
    ownStore.current = createChatStore({
      // Indirection, not the prop: the store keeps this object for its lifetime,
      // so reading the ref at call time is what lets the adapter change under a
      // transcript that must survive the change.
      adapter: { sendMessage: (request) => liveAdapter.current.sendMessage(withModel(request, liveModel.current)) },
      makeId: () => crypto.randomUUID(),
      now: () => Date.now(),
    });
  }

  // Per chat, and by ref for the same reason as the store: a listener that
  // outlived a re-created bus would hold a subscription nothing ever emits to —
  // silent, and indistinguishable from an event that simply did not happen.
  const events = useRef<ChatEvents | null>(null);
  events.current ??= createChatEvents();

  // A caller that SWAPS its store prop means it: that is the one identity we
  // must follow. Everything else is stable across renders.
  const active = store ?? ownStore.current;
  const value = useMemo(
    () => ({ store: active as ChatStore, capabilities, events: events.current as ChatEvents }),
    [active, capabilities],
  );

  // Where the surfaces are, for a host that must put the caret back or scope a
  // selection. Provided here because it spans BOTH — the composer and the
  // transcript — and a host asking is usually outside either.
  const surfaces = useSurfacesRegistry();
  useChatSounds(active as ChatStore, capabilities.sounds);

  return (
    <ChatContext.Provider value={value}>
      <ChatSurfacesContext.Provider value={surfaces}>{children}</ChatSurfacesContext.Provider>
    </ChatContext.Provider>
  );
}
