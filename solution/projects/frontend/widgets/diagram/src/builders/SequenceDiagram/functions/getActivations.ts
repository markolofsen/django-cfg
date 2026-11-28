/**
 * Activation builder functions for SequenceDiagram
 * @module Mermaid/builders/SequenceDiagram/functions/getActivations
 */

import { DiagramStore } from '../../core/DiagramStore';
import type { ActivationBuilder } from '../types';

/**
 * Create the activation builder for all participants
 */
export function createActivationBuilder<P extends string>(
  store: DiagramStore,
  participants: readonly P[],
): ActivationBuilder<P> {
  const builder = {} as ActivationBuilder<P>;

  participants.forEach((p) => {
    builder[p] = {
      activate() {
        store.add(`activate ${p}`);
      },
      deactivate() {
        store.add(`deactivate ${p}`);
      },
    };
  });

  return builder;
}
