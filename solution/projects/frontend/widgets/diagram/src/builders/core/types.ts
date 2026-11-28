/**
 * Shared types for Mermaid diagram builders
 * @module Mermaid/builders/core/types
 */

// ============================================================================
// Node Types
// ============================================================================

export type NodeId = string;

/**
 * Node shapes supported by Mermaid flowcharts
 * @see https://mermaid.js.org/syntax/flowchart.html#node-shapes
 */
export type NodeShape =
  | 'rect'           // [text]
  | 'round'          // (text)
  | 'stadium'        // ([text])
  | 'subroutine'     // [[text]]
  | 'cylinder'       // [(text)]
  | 'circle'         // ((text))
  | 'asymmetric'     // >text]
  | 'rhombus'        // {text}
  | 'hexagon'        // {{text}}
  | 'parallelogram'  // [/text/]
  | 'parallelogramAlt' // [\text\]
  | 'trapezoid'      // [/text\]
  | 'trapezoidAlt'   // [\text/]
  | 'doubleCircle';  // (((text)))

/**
 * Shape syntax lookup for Mermaid
 */
export const NODE_SHAPE_SYNTAX: Record<NodeShape, [string, string]> = {
  rect: ['[', ']'],
  round: ['(', ')'],
  stadium: ['([', '])'],
  subroutine: ['[[', ']]'],
  cylinder: ['[(', ')]'],
  circle: ['((', '))'],
  asymmetric: ['>', ']'],
  rhombus: ['{', '}'],
  hexagon: ['{{', '}}'],
  parallelogram: ['[/', '/]'],
  parallelogramAlt: ['[\\', '\\]'],
  trapezoid: ['[/', '\\]'],
  trapezoidAlt: ['[\\', '/]'],
  doubleCircle: ['(((', ')))'],
};

// ============================================================================
// Edge Types
// ============================================================================

/**
 * Edge line styles
 */
export type EdgeLineStyle = 'solid' | 'dotted' | 'thick';

/**
 * Arrow head types
 */
export type ArrowHead = 'arrow' | 'open' | 'circle' | 'cross' | 'none';

/**
 * Edge syntax lookup
 */
export const EDGE_SYNTAX: Record<EdgeLineStyle, Record<ArrowHead, string>> = {
  solid: {
    arrow: '-->',
    open: '---',
    circle: '--o',
    cross: '--x',
    none: '---',
  },
  dotted: {
    arrow: '-..->',
    open: '-.-',
    circle: '-.-o',
    cross: '-.-x',
    none: '-.-',
  },
  thick: {
    arrow: '==>',
    open: '===',
    circle: '==o',
    cross: '==x',
    none: '===',
  },
};

/**
 * Simplified edge syntax for common cases
 */
export const SIMPLE_EDGE_SYNTAX = {
  solid: '-->',
  dotted: '-.->',
  thick: '==>',
  solidOpen: '---',
  dottedOpen: '-.-',
} as const;

// ============================================================================
// Style Types
// ============================================================================

/**
 * CSS-like style properties for nodes
 */
export interface StyleProperties {
  fill?: string;
  stroke?: string;
  'stroke-width'?: string;
  color?: string;
  'font-weight'?: 'bold' | 'normal';
  'stroke-dasharray'?: string;
}

/**
 * Style class definition
 */
export interface StyleClass {
  name: string;
  properties: StyleProperties;
}

// ============================================================================
// Flow Diagram Types
// ============================================================================

/**
 * Flow diagram directions
 */
export type FlowDirection = 'TB' | 'BT' | 'LR' | 'RL';

// ============================================================================
// Sequence Diagram Types
// ============================================================================

/**
 * Participant types in sequence diagrams
 */
export type ParticipantType = 'participant' | 'actor';

/**
 * Message arrow types in sequence diagrams
 */
export const MESSAGE_ARROWS = {
  sync: '->>',        // Synchronous call
  syncReply: '-->>',  // Synchronous reply
  async: '-)',        // Async call
  asyncReply: '--)',  // Async reply
  solid: '->',        // Solid line
  dotted: '-->',      // Dotted line
  cross: '-x',        // Cross (failure)
  crossDotted: '--x', // Dotted cross
} as const;

export type MessageArrowType = keyof typeof MESSAGE_ARROWS;

// ============================================================================
// Journey Diagram Types
// ============================================================================

/**
 * Task score (1-5, where 5 is best)
 */
export type TaskScore = 1 | 2 | 3 | 4 | 5;

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Makes all properties in T writable (removes readonly)
 */
export type Writable<T> = { -readonly [P in keyof T]: T[P] };

/**
 * Extracts keys from a const object
 */
export type KeysOf<T> = keyof T & string;
