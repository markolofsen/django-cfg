/**
 * JourneyDiagram Builder
 * Declarative API for building Mermaid user journey diagrams
 * @module Mermaid/builders/JourneyDiagram/JourneyDiagram
 */

import { DiagramStore } from '../core/DiagramStore';
import type { TaskScore } from '../core/types';
import { sanitizeLabel } from '../core/sanitize';
import type { JourneyDiagramOptions, JourneyDiagramBuilder, SectionBuilder } from './types';

/**
 * Format actors for journey task
 */
function formatActors(actors: string | string[]): string {
  if (Array.isArray(actors)) {
    return actors.map(sanitizeLabel).join(', ');
  }
  return sanitizeLabel(actors);
}

/**
 * Create a JourneyDiagram builder
 *
 * @example
 * ```typescript
 * const journey = JourneyDiagram({ title: 'User Registration Flow' });
 *
 * journey.section('Discovery')
 *   .task('Visit website', 5, 'User')
 *   .task('Read about product', 4, 'User');
 *
 * journey.section('Registration')
 *   .task('Click sign up', 5, 'User')
 *   .task('Fill form', 2, 'User')
 *   .task('Verify email', 3, ['User', 'System']);
 *
 * journey.section('Onboarding')
 *   .task('Complete profile', 4, 'User')
 *   .task('Start using app', 5, 'User');
 *
 * console.log(journey.toString());
 * ```
 *
 * @param options - Diagram options (title is required)
 * @returns JourneyDiagram builder instance
 */
export function JourneyDiagram(options: JourneyDiagramOptions): JourneyDiagramBuilder {
  const store = new DiagramStore('journey');
  store.add(`title ${sanitizeLabel(options.title)}`);

  /**
   * Add a task line
   */
  const addTask = (name: string, score: TaskScore, actors: string | string[]) => {
    const actorStr = formatActors(actors);
    store.add(`${sanitizeLabel(name)}: ${score}: ${actorStr}`);
  };

  /**
   * Create a section builder for chaining tasks
   */
  const createSectionBuilder = (): SectionBuilder => ({
    task(name: string, score: TaskScore, actors: string | string[]) {
      addTask(name, score, actors);
      return this;
    },
  });

  return {
    section(name: string) {
      store.add(`section ${sanitizeLabel(name)}`);
      return createSectionBuilder();
    },

    task(name: string, score: TaskScore, actors: string | string[]) {
      addTask(name, score, actors);
    },

    comment(text: string) {
      store.addComment(text);
    },

    toString() {
      return store.toString();
    },
  };
}
