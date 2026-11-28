/**
 * Types for JourneyDiagram builder
 * @module Mermaid/builders/JourneyDiagram/types
 */

import type { TaskScore } from '../core/types';

/**
 * Options for JourneyDiagram builder
 */
export interface JourneyDiagramOptions {
  /** Diagram title */
  title: string;
}

/**
 * Task definition
 */
export interface TaskDefinition {
  /** Task name/description */
  name: string;
  /** Score (1-5, where 5 is best) */
  score: TaskScore;
  /** Actor(s) involved */
  actors: string | string[];
}

/**
 * Section builder interface
 */
export interface SectionBuilder {
  /** Add a task to the current section */
  task(name: string, score: TaskScore, actors: string | string[]): SectionBuilder;
}

/**
 * Main JourneyDiagram builder result
 */
export interface JourneyDiagramBuilder {
  /** Add a new section */
  section(name: string): SectionBuilder;
  /** Add a task directly (without section - goes to last section or creates implicit one) */
  task(name: string, score: TaskScore, actors: string | string[]): void;
  /** Add a comment */
  comment(text: string): void;
  /** Get the Mermaid string */
  toString(): string;
}
