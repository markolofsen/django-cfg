/**
 * Edge builder functions for FlowDiagram
 * @module Mermaid/builders/FlowDiagram/functions/getEdges
 */

import { DiagramStore } from '../../core/DiagramStore';
import { SIMPLE_EDGE_SYNTAX } from '../../core/types';
import { toNodeId, sanitizeLabel } from '../../core/sanitize';
import type { EdgeBuilder, EdgeEndBuilder } from '../types';

/**
 * Create an edge builder for a specific source node
 */
export function createEdgeBuilder<Nodes extends string>(
  store: DiagramStore,
  fromId: Nodes,
): EdgeBuilder<Nodes> {
  const safeFromId = toNodeId(fromId);

  return {
    to(toId: Nodes): EdgeEndBuilder {
      const safeToId = toNodeId(toId);

      const addEdge = (arrow: string, label?: string) => {
        if (label) {
          store.add(`${safeFromId} ${arrow}|${sanitizeLabel(label)}| ${safeToId}`);
        } else {
          store.add(`${safeFromId} ${arrow} ${safeToId}`);
        }
      };

      return {
        solid: (label) => addEdge(SIMPLE_EDGE_SYNTAX.solid, label),
        dotted: (label) => addEdge(SIMPLE_EDGE_SYNTAX.dotted, label),
        thick: (label) => addEdge(SIMPLE_EDGE_SYNTAX.thick, label),
        line: (label) => addEdge(SIMPLE_EDGE_SYNTAX.solidOpen, label),
        dottedLine: (label) => addEdge(SIMPLE_EDGE_SYNTAX.dottedOpen, label),
      };
    },
  };
}

/**
 * Create multiple edges at once (for convenience)
 */
export function createEdgesBuilder<Nodes extends string>(
  store: DiagramStore,
): (from: Nodes) => EdgeBuilder<Nodes> {
  return (from: Nodes) => createEdgeBuilder(store, from);
}
