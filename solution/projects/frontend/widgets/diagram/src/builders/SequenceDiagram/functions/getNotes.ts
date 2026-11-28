/**
 * Note builder functions for SequenceDiagram
 * @module Mermaid/builders/SequenceDiagram/functions/getNotes
 */

import { DiagramStore } from '../../core/DiagramStore';
import { sanitizeLabel } from '../../core/sanitize';
import type { NoteBuilder, NoteAction, NoteSideTarget, NoteOverTarget } from '../types';

/**
 * Create a single note action
 */
function createNoteAction(
  store: DiagramStore,
  position: string,
): NoteAction {
  return {
    msg(text: string) {
      store.add(`Note ${position}: ${sanitizeLabel(text)}`);
    },
  };
}

/**
 * Create note targets for left/right positions
 */
function createNoteSideTarget<P extends string>(
  store: DiagramStore,
  position: 'left' | 'right',
  participants: readonly P[],
): NoteSideTarget<P> {
  const target = {} as NoteSideTarget<P>;

  participants.forEach((p) => {
    target[p] = createNoteAction(store, `${position} of ${p}`);
  });

  return target;
}

/**
 * Create note targets for "over" position (can span multiple participants)
 */
function createNoteOverTarget<P extends string>(
  store: DiagramStore,
  participants: readonly P[],
): NoteOverTarget<P> {
  const target = {} as NoteOverTarget<P>;

  participants.forEach((first) => {
    // Create object with msg for single participant note
    const obj = {
      msg(text: string) {
        store.add(`Note over ${first}: ${sanitizeLabel(text)}`);
      },
    } as NoteAction & { [K in P]: NoteAction };

    // Add targets for spanning to other participants
    participants.forEach((second) => {
      if (first !== second) {
        (obj as Record<string, NoteAction>)[second] = {
          msg(text: string) {
            store.add(`Note over ${first},${second}: ${sanitizeLabel(text)}`);
          },
        };
      } else {
        // Self-reference just does single note
        (obj as Record<string, NoteAction>)[second] = {
          msg(text: string) {
            store.add(`Note over ${first}: ${sanitizeLabel(text)}`);
          },
        };
      }
    });

    target[first] = obj;
  });

  return target;
}

/**
 * Create the full note builder
 */
export function createNoteBuilder<P extends string>(
  store: DiagramStore,
  participants: readonly P[],
): NoteBuilder<P> {
  return {
    leftOf: createNoteSideTarget(store, 'left', participants),
    rightOf: createNoteSideTarget(store, 'right', participants),
    over: createNoteOverTarget(store, participants),
  };
}
