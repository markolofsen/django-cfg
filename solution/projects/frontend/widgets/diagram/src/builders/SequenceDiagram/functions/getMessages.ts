/**
 * Message builder functions for SequenceDiagram
 * @module Mermaid/builders/SequenceDiagram/functions/getMessages
 */

import { DiagramStore } from '../../core/DiagramStore';
import { MESSAGE_ARROWS } from '../../core/types';
import { sanitizeLabel } from '../../core/sanitize';
import type { MessageBuilder, MessageAction, MessageTarget, MessageArrows } from '../types';

/**
 * Create message actions for a specific from -> arrow -> to combination
 */
function createMessageAction(
  store: DiagramStore,
  from: string,
  arrow: string,
  to: string,
): MessageAction {
  return {
    msg(text: string) {
      store.add(`${from}${arrow}${to}: ${sanitizeLabel(text)}`);
    },
    activate(text: string) {
      store.add(`${from}${arrow}+${to}: ${sanitizeLabel(text)}`);
    },
    deactivate(text: string) {
      store.add(`${from}${arrow}-${to}: ${sanitizeLabel(text)}`);
    },
  };
}

/**
 * Create message target for a specific from -> arrow combination
 */
function createMessageTarget<P extends string>(
  store: DiagramStore,
  from: string,
  arrow: string,
  participants: readonly P[],
): MessageTarget<P> {
  const target = {} as MessageTarget<P>;

  participants.forEach((to) => {
    target[to] = createMessageAction(store, from, arrow, to);
  });

  return target;
}

/**
 * Create arrow selector for a specific from participant
 */
function createMessageArrows<P extends string>(
  store: DiagramStore,
  from: P,
  participants: readonly P[],
): MessageArrows<P> {
  return {
    sync: createMessageTarget(store, from, MESSAGE_ARROWS.sync, participants),
    syncReply: createMessageTarget(store, from, MESSAGE_ARROWS.syncReply, participants),
    async: createMessageTarget(store, from, MESSAGE_ARROWS.async, participants),
    asyncReply: createMessageTarget(store, from, MESSAGE_ARROWS.asyncReply, participants),
    solid: createMessageTarget(store, from, MESSAGE_ARROWS.solid, participants),
    dotted: createMessageTarget(store, from, MESSAGE_ARROWS.dotted, participants),
    cross: createMessageTarget(store, from, MESSAGE_ARROWS.cross, participants),
    crossDotted: createMessageTarget(store, from, MESSAGE_ARROWS.crossDotted, participants),
  };
}

/**
 * Create the full message builder for all participants
 */
export function createMessageBuilder<P extends string>(
  store: DiagramStore,
  participants: readonly P[],
): MessageBuilder<P> {
  const builder = {} as MessageBuilder<P>;

  participants.forEach((from) => {
    builder[from] = createMessageArrows(store, from, participants);
  });

  return builder;
}
