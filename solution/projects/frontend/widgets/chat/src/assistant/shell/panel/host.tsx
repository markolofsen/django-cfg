'use client';

import { createContext, useContext, useEffect, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { createPortal } from 'react-dom';

/**
 * One mounted chat, many places. The chat is rendered through a portal into one detached element (`AssistantPortal`); a surface (`AssistantSlot`) attaches that
 * element where it is visible and parks it when it unmounts. Navigating or switching surface while a run streams therefore never unmounts the chat:
 * nothing is aborted and the thread state is not rebuilt. `AssistantHostProvider` wraps the page tree once, in the layout.
 */
interface HostValue {
  element: HTMLElement;
  park: HTMLElement;
}
const HostContext = createContext<HostValue | null>(null);
/** The header controls the conversation publishes (`AssistantHeaderActions`), and the stable setter it publishes them with. Two contexts: the publisher must not re-render when they change. */
const ActionsContext = createContext<ReactNode>(null);
const SetActionsContext = createContext<((actions: ReactNode) => void) | null>(null);
/** The history screen: whether it is shown, and what it is (published by `AssistantHistory`). */
interface HistoryValue {
  open: boolean;
  setOpen: (open: boolean) => void;
  panel: ReactNode;
  setPanel: (panel: ReactNode) => void;
}
const HistoryContext = createContext<HistoryValue | null>(null);

export function AssistantHostProvider({ children }: { children: ReactNode }) {
  // Browser only: on the server there is no element, and slots render empty.
  const value = useMemo<HostValue | null>(() => {
    if (typeof document === 'undefined') return null;
    const element = document.createElement('div');
    element.className = 'h-full min-h-0';
    const park = document.createElement('div');
    park.hidden = true;
    park.appendChild(element);
    return { element, park };
  }, []);

  useEffect(() => {
    if (!value) return;
    document.body.appendChild(value.park);
    return () => value.park.remove();
  }, [value]);

  const [actions, setActions] = useState<ReactNode>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [panel, setPanel] = useState<ReactNode>(null);
  const history = useMemo<HistoryValue>(() => ({ open: historyOpen, setOpen: setHistoryOpen, panel, setPanel }), [historyOpen, panel]);
  return (
    <HistoryContext.Provider value={history}>
    <HostContext.Provider value={value}>
      <SetActionsContext.Provider value={setActions}>
        <ActionsContext.Provider value={actions}>{children}</ActionsContext.Provider>
      </SetActionsContext.Provider>
    </HostContext.Provider>
    </HistoryContext.Provider>
  );
}

/** Renders the chat (`children`) into the host element. Mount it once, for a signed-in viewer, inside the provider. */
export function AssistantPortal({ children }: { children: ReactNode }) {
  const host = useContext(HostContext);
  return host ? createPortal(children, host.element) : null;
}

/** A place that shows the chat: an empty box the chat element is moved into while the slot is mounted. */
export function AssistantSlot({ className }: { className?: string }) {
  const host = useContext(HostContext);
  const box = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    if (!host || !box.current) return;
    const place = box.current;
    place.appendChild(host.element);
    return () => {
      if (host.element.parentElement === place) host.park.appendChild(host.element);
    };
  }, [host]);
  const history = useContext(HistoryContext);
  const showing = history?.open === true && history.panel != null;
  return (
    <div className={`relative ${className ?? ''}`}>
      {/* The chat stays mounted under the history screen (a run keeps streaming); `inert` keeps its composer out of the tab order and away from a screen reader meanwhile. */}
      <div ref={box} className="h-full min-h-0" inert={showing || undefined} />
      {showing ? <div className="absolute inset-0 z-10 bg-background">{history.panel}</div> : null}
    </div>
  );
}

/**
 * Publishes the history screen (`panel`) to the slot, which draws it over the conversation while the history is open. Call it from wherever the session is, beside `AssistantPortal`
 * (the assistant entry's `AssistantHistory` builds the `SessionsPanel` and calls this); `null` draws nothing. Without a provider it does nothing.
 */
export function usePublishHistoryPanel(panel: ReactNode): void {
  const history = useContext(HistoryContext);
  const setPanel = history?.setPanel;
  const setOpen = history?.setOpen;
  useEffect(() => {
    setPanel?.(panel);
  }, [setPanel, panel]);
  useEffect(() => () => {
    setPanel?.(null);
    setOpen?.(false);
  }, [setPanel, setOpen]);
}

/** Whether the history screen is open and how to change it; `null` outside `AssistantHostProvider`. */
export function useAssistantHistory(): { open: boolean; setOpen: (open: boolean) => void } | null {
  const history = useContext(HistoryContext);
  return history ? { open: history.open, setOpen: history.setOpen } : null;
}

/**
 * Publishes the header controls (`<SessionsMenu session={session} />`) from wherever the conversation is mounted. `AssistantFrame` and `ChatDock` show them next to Close
 * without the host passing them through its component tree: the column, the dock and the conversation are usually three different files. Render it beside `AssistantPortal`.
 * An explicit `actions` prop on the frame or the dock still wins.
 */
export function AssistantHeaderActions({ children }: { children: ReactNode }) {
  const set = useContext(SetActionsContext);
  useEffect(() => {
    set?.(children);
  }, [set, children]);
  useEffect(() => () => set?.(null), [set]);
  return null;
}

/** The controls published by `AssistantHeaderActions`, or null. */
export function useHeaderActions(): ReactNode {
  return useContext(ActionsContext);
}
