/**
 * Types for SequenceDiagram builder
 * @module Mermaid/builders/SequenceDiagram/types
 */

import type { ParticipantType } from '../core/types';

/**
 * Participants definition object
 */
export type ParticipantsObject<P extends string> = {
  readonly [K in P]: ParticipantType | { type: ParticipantType; alias?: string };
};

/**
 * Options for SequenceDiagram builder
 */
export interface SequenceDiagramOptions {
  /** Enable auto-numbering of messages */
  autoNumber?: boolean;
}

/**
 * Message action builder
 */
export interface MessageAction {
  /** Add a message with text */
  msg(text: string): void;
  /** Add a message that activates the target */
  activate(text: string): void;
  /** Add a message that deactivates the target */
  deactivate(text: string): void;
}

/**
 * Target participant selector for messages
 */
export type MessageTarget<P extends string> = {
  [K in P]: MessageAction;
};

/**
 * Arrow type selector for messages
 */
export type MessageArrows<P extends string> = {
  /** Synchronous call ->> */
  sync: MessageTarget<P>;
  /** Synchronous reply -->> */
  syncReply: MessageTarget<P>;
  /** Async call -) */
  async: MessageTarget<P>;
  /** Async reply --) */
  asyncReply: MessageTarget<P>;
  /** Solid line -> */
  solid: MessageTarget<P>;
  /** Dotted line --> */
  dotted: MessageTarget<P>;
  /** Cross (failure) -x */
  cross: MessageTarget<P>;
  /** Dotted cross --x */
  crossDotted: MessageTarget<P>;
};

/**
 * Message builder - from participant to arrow type to target
 */
export type MessageBuilder<P extends string> = {
  [K in P]: MessageArrows<P>;
};

/**
 * Note position types
 */
export type NotePosition = 'leftOf' | 'rightOf' | 'over';

/**
 * Single note action
 */
export interface NoteAction {
  msg(text: string): void;
}

/**
 * Note target for "over" position (can span multiple participants)
 */
export type NoteOverTarget<P extends string> = {
  [K in P]: NoteAction & {
    /** Span to another participant */
    [K2 in P]: NoteAction;
  };
};

/**
 * Note target for left/right positions
 */
export type NoteSideTarget<P extends string> = {
  [K in P]: NoteAction;
};

/**
 * Note builder
 */
export interface NoteBuilder<P extends string> {
  leftOf: NoteSideTarget<P>;
  rightOf: NoteSideTarget<P>;
  over: NoteOverTarget<P>;
}

/**
 * Activation builder
 */
export type ActivationBuilder<P extends string> = {
  [K in P]: {
    activate(): void;
    deactivate(): void;
  };
};

/**
 * Arrow type for dynamic message method
 */
export type DynamicArrowType = 'sync' | 'syncReply' | 'async' | 'asyncReply' | 'solid' | 'dotted' | 'cross' | 'crossDotted';

/**
 * Main SequenceDiagram builder result
 */
export interface SequenceDiagramBuilder<P extends string> {
  /** Message builder (d.Alice.sync.Bob.msg("Hello")) */
  d: MessageBuilder<P>;
  /** Note builder (note.over.Alice.msg("Thinking")) */
  note: NoteBuilder<P>;
  /** Activation builder (activate.Alice.activate()) */
  activate: ActivationBuilder<P>;

  // ============================================================================
  // Dynamic access methods (for runtime participant names)
  // ============================================================================

  /**
   * Send a message dynamically (for runtime participant names)
   * @example message('Alice', 'Bob', 'Hello!') // sync arrow
   * @example message('Alice', 'Bob', 'Hello!', 'async')
   */
  message(from: string, to: string, text: string, arrow?: DynamicArrowType): void;

  /**
   * Add a note over one participant dynamically
   * @example noteOver('Alice', 'Thinking...')
   */
  noteOver(participant: string, text: string): void;

  /**
   * Add a note spanning two participants dynamically
   * @example noteOverSpan('Alice', 'Bob', 'Handshake')
   */
  noteOverSpan(participant1: string, participant2: string, text: string): void;

  /**
   * Add a note to the left of a participant
   * @example noteLeft('Alice', 'Waiting')
   */
  noteLeft(participant: string, text: string): void;

  /**
   * Add a note to the right of a participant
   * @example noteRight('Alice', 'Done')
   */
  noteRight(participant: string, text: string): void;

  // ============================================================================
  // Block methods
  // ============================================================================

  /** Loop block */
  loop(label: string, fn: () => void): void;
  /** Optional/alternative block */
  alt(label: string, fn: () => void): { else(label: string, fn: () => void): void };
  /** Parallel block */
  par(label: string, fn: () => void): { and(label: string, fn: () => void): void };
  /** Colored rectangle box */
  rect(color: string, fn: () => void): void;
  /** Critical region */
  critical(label: string, fn: () => void): { option(label: string, fn: () => void): void };
  /** Break */
  break(label: string, fn: () => void): void;
  /** Add a comment */
  comment(text: string): void;
  /** Add blank line */
  blank(): void;
  /** Get the Mermaid string */
  toString(): string;
}
