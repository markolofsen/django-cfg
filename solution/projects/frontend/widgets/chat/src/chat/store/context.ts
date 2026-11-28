/**
 * The single context.
 *
 * Capabilities ride here rather than being threaded as props, which is what
 * lets `<Chat>` stay at seven props while a composer three levels down still
 * knows which features exist. One context, not one per feature: a context per
 * capability would put the count back on the same growth curve the props were
 * on.
 */

import { createContext } from "react";

import type { ChatCapabilities } from "../core/capabilities";
import type { ChatEvents } from "../core/conversation/events";
import type { ChatStore } from "./store";

export interface ChatContextValue {
  readonly store: ChatStore;
  readonly capabilities: ChatCapabilities;
  /**
   * Announcements, as opposed to state. The store answers "what is true now";
   * this says "this just happened" — which a subscriber cannot reconstruct from
   * a snapshot, because two identical states can be reached by different acts.
   */
  readonly events: ChatEvents;
}

export const ChatContext = createContext<ChatContextValue | null>(null);
