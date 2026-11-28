import { createContext, useContext, useMemo, type ReactNode } from "react";

import type { ChatMessage, MessagePart, RunPart } from "../../core/conversation/parts";

export interface PartRenderProps {
  /** A message part, or the render-only `run` segment (adjacent steps) when a host registered a `run` renderer. */
  readonly part: MessagePart | RunPart;
  readonly message: ChatMessage;
}

export type PartRenderer = (props: PartRenderProps) => ReactNode;

/** `type` → renderer. Unregistered types render nothing rather than crashing. */
export type PartRegistry = Readonly<Record<string, PartRenderer>>;

const PartRegistryContext = createContext<PartRegistry>({});

export interface PartRegistryProviderProps {
  readonly renderers: PartRegistry;
  readonly children: ReactNode;
}

/**
 * Registry of part renderers, inherited by nested threads.
 *
 * Inheritance is the load-bearing part, and it is why this is a context rather
 * than a prop. A subagent's transcript renders inside a tool part; without
 * inheritance every host would have to re-register the same renderers at every
 * nesting level, and the ones they forgot would silently render nothing.
 * assistant-ui reached the same conclusion.
 *
 * Nesting MERGES rather than replaces, so a nested thread can override one
 * renderer — a compact tool card, say — without losing the rest.
 */
export function PartRegistryProvider({ renderers, children }: PartRegistryProviderProps) {
  const inherited = useContext(PartRegistryContext);
  const merged = useMemo(() => ({ ...inherited, ...renderers }), [inherited, renderers]);
  return (
    <PartRegistryContext.Provider value={merged}>{children}</PartRegistryContext.Provider>
  );
}

export function usePartRenderer(type: string): PartRenderer | undefined {
  return useContext(PartRegistryContext)[type];
}
