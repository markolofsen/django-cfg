import { useEffect, useRef, type ReactNode } from "react";

import type { ChatAdapter } from "../../core/conversation/adapter";
import type { ChatCapabilities } from "../../core/capabilities";
import type { ChatMessage } from "../../core/conversation/parts";
import { ChatProvider, useChatStore } from "../../store";
import { PartRegistryProvider, type PartRegistry } from "../../primitives";
import { ChatComposer } from "./composer";
import { ChatTranscript } from "../transcript/transcript";

/**
 * The packaged chat.
 *
 * SEVEN props, and that number is the whole design. The predecessor reached 83,
 * each documented "omit ⇒ feature off", which produced a configuration space no
 * one could enumerate and bugs that lived in untested combinations. Here a
 * feature arrives as a capability, a part renderer, or a slot — never as a
 * prop, so the count does not move as the product grows
 * (`@rules/architecture.md`).
 *
 * `<Chat>` is a convenience, not the API. A host that needs a different layout
 * drops to `<ChatProvider>` plus primitives and keeps every behaviour; that
 * escape hatch is what keeps this component from accreting props for layouts it
 * was never meant to cover.
 */
interface ChatBase {
  readonly adapter: ChatAdapter;
  /** Present ⇒ the feature exists. There is no boolean to contradict it. */
  readonly capabilities?: ChatCapabilities;
  /** `part.type` → renderer. Absent types render nothing rather than crashing. */
  readonly renderers?: PartRegistry;
  /** Which conversation this is, and the turns it opens with. */
  readonly conversation?: ChatConversation;
  /** Named insertion points: `header`, `toolbarEnd`, `footer`, `messageFooter`. */
  readonly slots?: ChatSlots;
  readonly className?: string;
}

/**
 * Seven props, counted honestly — the budget test reads this file.
 *
 * `body` stays ONE prop rather than a `children` beside a boolean: the packaged
 * layout and a host's own composition are mutually exclusive, so they were
 * never two decisions. One prop, one union, both mistakes unrepresentable.
 */
export interface ChatProps extends ChatBase {
  readonly body: ChatBody;
}

/**
 * The conversation on screen: which room, and the turns it opens with.
 *
 * ONE prop rather than `history` beside a `room`, because they are one
 * decision. A host never changes the room without changing the turns, and the
 * two arriving separately is what made "the conversation changed" a thing the
 * store had to INFER from a new array identity — an inference that covered the
 * transcript and silently missed the rest of the room's state.
 *
 * `id` is what the store compares. Omit it and the seam behaves exactly as the
 * bare history array did: a new array reseeds the transcript and nothing else.
 * Supply it and a room change also clears what belongs to the room it left.
 */
export interface ChatConversation {
  /**
   * Stable identity of the room. Any spelling the host likes, as long as two
   * different rooms never share one — it is compared, never parsed.
   */
  readonly id?: string;
  /** Prior turns to seed. `undefined` = not loaded yet, `[]` = empty room. */
  readonly history?: readonly ChatMessage[];
}

export interface ChatSlots {
  readonly header?: ReactNode;
  readonly toolbarEnd?: ReactNode;
  readonly footer?: ReactNode;
  /**
   * The per-message action row. A slot, not a label: WHICH actions exist is the
   * host's inventory, and a flag per action could never express one the package
   * has not heard of.
   */
  readonly messageFooter?: (message: ChatMessage) => ReactNode;
}

const noRenderers: PartRegistry = {};

export function Chat({
  adapter,
  capabilities,
  renderers = noRenderers,
  conversation,
  slots,
  className,
  body,
}: ChatProps) {
  return (
    <ChatProvider adapter={adapter} capabilities={capabilities}>
      <PartRegistryProvider renderers={renderers}>
        <ChatLayout
          conversation={conversation}
          slots={slots}
          className={className}
          {...body}
        />
      </PartRegistryProvider>
    </ChatProvider>
  );
}

/**
 * What fills the chat: the packaged layout, or the host's own composition.
 *
 * `packaged` needs no payload — the copy comes from the package's own
 * dictionary, so there is nothing left for a host to supply.
 */
export type ChatBody =
  | { readonly kind: "packaged" }
  | { readonly kind: "custom"; readonly children: ReactNode };

type ChatLayoutProps = {
  readonly conversation?: ChatConversation;
  readonly slots?: ChatSlots;
  readonly className?: string;
} & ChatBody;

/**
 * Inside the provider, because seeding needs the store.
 *
 * A custom body REPLACES the default rather than adding to it: a host passing
 * its own composition wants exactly that, and merging the two would make every
 * custom layout start by hiding parts of the default one.
 */
function ChatLayout({ conversation, slots, className, ...body }: ChatLayoutProps) {
  useConversation(conversation);

  return (
    // `relative` is stated here rather than left to the host's `className`: the
    // surfaces that position against this pane are this component's own
    // children, so a host that forgot it would have them resolve against the
    // viewport and cover the whole page.
    <div className={`relative ${className ?? ""}`}>
      {slots?.header}
      {body.kind === "custom" ? (
        body.children
      ) : (
        <>
          <ChatTranscript footer={slots?.messageFooter} />
          <ChatComposer toolbarEnd={slots?.toolbarEnd} />
        </>
      )}
      {slots?.footer}
    </div>
  );
}

/**
 * Seed the transcript, and leave the previous room behind when the room changes.
 *
 * Seeding is keyed on array identity, not contents: `load` replaces the
 * transcript wholesale, so running it on every render would discard a live turn.
 * A host that appends to its history array gets one reload, which is the
 * intended behaviour.
 *
 * The ROOM change is a separate signal and does more, because `load` only ever
 * replaced the transcript. A room also owns its queued prompts and its in-flight
 * turn, and both used to survive on the host's mount — which is why hosts
 * destroyed the whole chat on every switch. Without this reset, dropping that
 * remount would carry one room's "thinking" indicator and another room's queued
 * text into the conversation the user just opened.
 *
 * Ordering is load-bearing: the reset runs BEFORE the seed, in one effect rather
 * than two. Two effects would fire in declaration order on the first render of a
 * new room and blank the transcript the seed had just placed.
 */
function useConversation(conversation: ChatConversation | undefined): void {
  const store = useChatStore();
  const history = conversation?.history;
  const roomId = conversation?.id;
  // The room this store is currently showing. A ref, not state: nothing renders
  // from it, and it must be readable and writable inside the same effect pass.
  const shownRoom = useRef(roomId);

  useEffect(() => {
    if (shownRoom.current !== roomId) {
      shownRoom.current = roomId;
      // Aborts an in-flight turn and drops the queue. A turn belongs to the room
      // it was sent to; abandoning it silently is what already happened when the
      // host remounted, so this preserves the behaviour rather than changing it.
      store.leaveRoom();
    }
    // `undefined` is "not loaded yet", and the store must be told: a transcript
    // that only knows "no messages" shows the empty state during the fetch, so
    // a room with 90 replies opened on an empty state for ~100ms.
    store.setHistoryLoaded(history !== undefined);
    if (history !== undefined) store.load(history);
  }, [history, roomId, store]);
}
