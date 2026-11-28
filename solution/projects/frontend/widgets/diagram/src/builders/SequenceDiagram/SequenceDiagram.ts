/**
 * SequenceDiagram Builder
 * Declarative API for building Mermaid sequence diagrams
 * @module Mermaid/builders/SequenceDiagram/SequenceDiagram
 */

import { DiagramStore } from '../core/DiagramStore';
import type { ParticipantType } from '../core/types';
import { sanitizeLabel } from '../core/sanitize';
import { createMessageBuilder } from './functions/getMessages';
import { createNoteBuilder } from './functions/getNotes';
import { createActivationBuilder } from './functions/getActivations';
import {
  createLoopBuilder,
  createAltBuilder,
  createParBuilder,
  createRectBuilder,
  createCriticalBuilder,
  createBreakBuilder,
} from './functions/getBlocks';
import type { ParticipantsObject, SequenceDiagramOptions, SequenceDiagramBuilder, DynamicArrowType } from './types';

const DEFAULT_OPTIONS: Required<SequenceDiagramOptions> = {
  autoNumber: false,
};

/**
 * Normalize participant definition to { type, alias } format
 */
function normalizeParticipant(
  value: ParticipantType | { type: ParticipantType; alias?: string },
): { type: ParticipantType; alias?: string } {
  if (typeof value === 'string') {
    return { type: value };
  }
  return value;
}

/**
 * Create a SequenceDiagram builder
 *
 * @example
 * ```typescript
 * const { d, note, loop, rect } = SequenceDiagram({
 *   Alice: 'participant',
 *   Bob: 'actor',
 *   Charlie: { type: 'participant', alias: 'C' },
 * }, { autoNumber: true });
 *
 * rect('rgb(200, 220, 255)', () => {
 *   d.Alice.sync.Bob.msg('Hello!');
 *   d.Bob.syncReply.Alice.msg('Hi there!');
 * });
 *
 * loop('Every minute', () => {
 *   d.Alice.async.Charlie.msg('Ping');
 * });
 *
 * note.over.Alice.Bob.msg('Handshake complete');
 *
 * console.log(toString());
 * ```
 *
 * @param participants - Participant definitions
 * @param options - Diagram options
 * @returns SequenceDiagram builder instance
 */
export function SequenceDiagram<P extends string>(
  participants: ParticipantsObject<P>,
  options: SequenceDiagramOptions = {},
): SequenceDiagramBuilder<P> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const store = new DiagramStore('sequenceDiagram');

  // Add autonumber if requested
  if (opts.autoNumber) {
    store.add('autonumber');
  }

  // Get participant keys
  const participantKeys = Object.keys(participants) as P[];

  // Declare participants
  store.addBlank();
  participantKeys.forEach((key) => {
    const def = normalizeParticipant(participants[key]);
    if (def.alias) {
      store.add(`${def.type} ${key} as ${sanitizeLabel(def.alias)}`);
    } else {
      store.add(`${def.type} ${key}`);
    }
  });
  store.addBlank();

  // Create builders
  const messageBuilder = createMessageBuilder<P>(store, participantKeys);
  const noteBuilder = createNoteBuilder<P>(store, participantKeys);
  const activationBuilder = createActivationBuilder<P>(store, participantKeys);

  // Arrow type to Mermaid syntax mapping
  const arrowMap: Record<DynamicArrowType, string> = {
    sync: '->>',
    syncReply: '-->>',
    async: '-)',
    asyncReply: '--)',
    solid: '->',
    dotted: '-->',
    cross: '-x',
    crossDotted: '--x',
  };

  return {
    d: messageBuilder,
    note: noteBuilder,
    activate: activationBuilder,

    // Dynamic access methods
    message(from: string, to: string, text: string, arrow: DynamicArrowType = 'sync') {
      const arrowSyntax = arrowMap[arrow] || '->>';
      store.add(`${from}${arrowSyntax}${to}: ${sanitizeLabel(text)}`);
    },

    noteOver(participant: string, text: string) {
      store.add(`Note over ${participant}: ${sanitizeLabel(text)}`);
    },

    noteOverSpan(participant1: string, participant2: string, text: string) {
      store.add(`Note over ${participant1},${participant2}: ${sanitizeLabel(text)}`);
    },

    noteLeft(participant: string, text: string) {
      store.add(`Note left of ${participant}: ${sanitizeLabel(text)}`);
    },

    noteRight(participant: string, text: string) {
      store.add(`Note right of ${participant}: ${sanitizeLabel(text)}`);
    },

    loop: createLoopBuilder(store),
    alt: createAltBuilder(store),
    par: createParBuilder(store),
    rect: createRectBuilder(store),
    critical: createCriticalBuilder(store),
    break: createBreakBuilder(store),

    comment(text: string) {
      store.addComment(text);
    },

    blank() {
      store.addBlank();
    },

    toString() {
      return store.toString();
    },
  };
}
