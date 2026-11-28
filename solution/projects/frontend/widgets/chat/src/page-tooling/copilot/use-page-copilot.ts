"use client";

import { useCallback, useRef } from "react";

import type { ChatAdapter } from "../../chat/core";
import { usePageSnapshot } from "../page-snapshot";
import {
  withPageContext,
  type ActionResult,
  type PageAwareAdapter,
} from "./adapter";
import { contextHash, readPageContext } from "./context";

export interface PageCopilot {
  /** The host's adapter, wrapped so every turn carries the page. */
  readonly adapter: ChatAdapter;
  /** Record what became of a proposed action; it rides the next turn. */
  readonly reportResult: (result: ActionResult) => void;
}

/**
 * Give a chat the page it is looking at.
 *
 * Returns the host's own adapter, wrapped. Nothing else changes: the chat gets
 * no new prop, no capability, and no knowledge that this exists.
 *
 * Must be rendered inside `PageSnapshotProvider`, which owns the opt-in and the
 * capture.
 */
export function usePageCopilot(adapter: PageAwareAdapter): PageCopilot {
  const snapshot = usePageSnapshot();

  // Per hook instance, not per module: two chats on one page each track what
  // THEY last sent, and a module-level baseline would have one silence the
  // other's first snapshot.
  const lastHash = useRef<string | null>(null);
  const pending = useRef<ActionResult[]>([]);

  const readPage = useCallback(() => {
    const context = readPageContext(snapshot, lastHash.current);
    if (context) lastHash.current = contextHash(context);
    return context;
  }, [snapshot]);

  const drainResults = useCallback((): readonly ActionResult[] => {
    const drained = pending.current;
    pending.current = [];
    return drained;
  }, []);

  const reportResult = useCallback((result: ActionResult) => {
    pending.current = [...pending.current, result];
  }, []);

  // One ref holding everything the wrapper reads, refreshed each render. The
  // wrapper itself is created once: the chat keeps its adapter for the life of
  // the store, so an identity that changed per render would be captured stale
  // — and a wrapper that reads through a ref never is.
  const live = useRef({ adapter, readPage, drainResults });
  live.current = { adapter, readPage, drainResults };

  const wrapped = useRef<ChatAdapter | null>(null);
  wrapped.current ??= withPageContext(
    {
      sendMessage: (request, turn) => live.current.adapter.sendMessage(request, turn),
    },
    {
      readPage: () => live.current.readPage(),
      drainResults: () => live.current.drainResults(),
    }
  );

  return { adapter: wrapped.current, reportResult };
}
