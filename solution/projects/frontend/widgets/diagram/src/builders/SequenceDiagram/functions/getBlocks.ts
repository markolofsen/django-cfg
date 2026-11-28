/**
 * Block builder functions for SequenceDiagram (loop, alt, par, rect, etc.)
 * @module Mermaid/builders/SequenceDiagram/functions/getBlocks
 */

import { DiagramStore } from '../../core/DiagramStore';
import { sanitizeLabel } from '../../core/sanitize';

/**
 * Create a loop block builder
 */
export function createLoopBuilder(store: DiagramStore) {
  return (label: string, fn: () => void) => {
    store.add(`loop ${sanitizeLabel(label)}`);
    store.indent();
    fn();
    store.dedent();
    store.add('end');
  };
}

/**
 * Create an alt (alternative/conditional) block builder
 */
export function createAltBuilder(store: DiagramStore) {
  return (label: string, fn: () => void) => {
    store.add(`alt ${sanitizeLabel(label)}`);
    store.indent();
    fn();
    store.dedent();

    return {
      else(elseLabel: string, elseFn: () => void) {
        store.add(`else ${sanitizeLabel(elseLabel)}`);
        store.indent();
        elseFn();
        store.dedent();
        store.add('end');
      },
    };
  };
}

/**
 * Create a parallel (par) block builder
 */
export function createParBuilder(store: DiagramStore) {
  return (label: string, fn: () => void) => {
    store.add(`par ${sanitizeLabel(label)}`);
    store.indent();
    fn();
    store.dedent();

    return {
      and(andLabel: string, andFn: () => void) {
        store.add(`and ${sanitizeLabel(andLabel)}`);
        store.indent();
        andFn();
        store.dedent();
        store.add('end');
      },
    };
  };
}

/**
 * Create a rect (colored box) block builder
 */
export function createRectBuilder(store: DiagramStore) {
  return (color: string, fn: () => void) => {
    store.add(`rect ${color}`);
    store.indent();
    fn();
    store.dedent();
    store.add('end');
  };
}

/**
 * Create a critical region block builder
 */
export function createCriticalBuilder(store: DiagramStore) {
  return (label: string, fn: () => void) => {
    store.add(`critical ${sanitizeLabel(label)}`);
    store.indent();
    fn();
    store.dedent();

    return {
      option(optionLabel: string, optionFn: () => void) {
        store.add(`option ${sanitizeLabel(optionLabel)}`);
        store.indent();
        optionFn();
        store.dedent();
        store.add('end');
      },
    };
  };
}

/**
 * Create a break block builder
 */
export function createBreakBuilder(store: DiagramStore) {
  return (label: string, fn: () => void) => {
    store.add(`break ${sanitizeLabel(label)}`);
    store.indent();
    fn();
    store.dedent();
    store.add('end');
  };
}
