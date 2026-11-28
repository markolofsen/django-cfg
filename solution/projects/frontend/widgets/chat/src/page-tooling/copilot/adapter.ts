/**
 * The seam: an adapter that carries the page with the turn.
 *
 * `ChatAdapter` is the host's interface — one method, a request in, a stream
 * out. The copilot needs neither a field on `SendRequest` nor a capability on
 * `<Chat>`: it wraps whatever adapter the host already has, so the chat is
 * untouched and a host without the copilot sends exactly what it sends now.
 *
 * Wrapping also keeps the snapshot out of the transcript. A `DataPart` would
 * put a serialised DOM tree in `history`, and every later turn would re-send
 * every earlier capture.
 */

import type { ActionOutcome } from "../browser-bridge/perform";
import type { ChatAdapter, SendRequest, StreamChunk } from "../../chat/core";
import type { PageContext } from "./context";

/**
 * What the host's adapter receives alongside the turn.
 *
 * A second argument, not a widened request: the request is the chat's shape
 * and stays exactly as the chat built it.
 */
export interface PageTurn {
  /** The page as the agent will see it, or absent when not shared. */
  readonly page?: PageContext;
  /** Outcomes of actions the agent proposed on the previous turn. */
  readonly results?: readonly ActionResult[];
}

/** What became of one proposed action. */
export interface ActionResult {
  readonly actionId: string;
  readonly outcome: ActionOutcome;
}

// Defined where it is produced — `browser-bridge` runs the action and decides
// the outcome, so the vocabulary is its, not the chat wiring's.
export type { ActionOutcome };

/** A host adapter that also accepts the page. */
export interface PageAwareAdapter {
  sendMessage(request: SendRequest, turn: PageTurn): Promise<ReadableStream<StreamChunk>>;
}

/** Everything the wrapper needs, gathered per send. */
export interface TurnSource {
  /** The page to send, or undefined when the user has not opted in. */
  readPage: () => PageContext | undefined;
  /** Outcomes accumulated since the last send; cleared by reading them. */
  drainResults: () => readonly ActionResult[];
}

/**
 * Wrap a page-aware adapter so it satisfies the chat's plain `ChatAdapter`.
 *
 * The chat calls one method with its own request; the wrapper reads the page at
 * that moment — capture-on-send, never on a timer — and hands both to the host.
 */
export function withPageContext(adapter: PageAwareAdapter, source: TurnSource): ChatAdapter {
  return {
    sendMessage(request) {
      const page = source.readPage();
      const results = source.drainResults();
      return adapter.sendMessage(request, {
        ...(page ? { page } : {}),
        ...(results.length > 0 ? { results } : {}),
      });
    },
  };
}
