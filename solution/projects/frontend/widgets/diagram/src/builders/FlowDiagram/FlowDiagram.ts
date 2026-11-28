/**
 * FlowDiagram Builder
 * Declarative API for building Mermaid flowchart diagrams
 * @module Mermaid/builders/FlowDiagram/FlowDiagram
 */

import { DiagramStore } from '../core/DiagramStore';
import type { FlowDirection } from '../core/types';
import { createNodeBuilder } from './functions/getNodes';
import { createEdgeBuilder } from './functions/getEdges';
import { createStyleBuilder } from './functions/getStyles';
import type {
  FlowDiagramOptions,
  FlowDiagramBuilder,
  SubgraphBuilder,
  NodeBuilder,
} from './types';

const DEFAULT_OPTIONS: Required<FlowDiagramOptions> = {
  direction: 'TB',
};

/**
 * Create a FlowDiagram builder
 *
 * @example
 * ```typescript
 * const flow = FlowDiagram<'A' | 'B' | 'C'>({ direction: 'LR' });
 *
 * flow.node('A').rect('Start');
 * flow.node('B').circle('Process');
 * flow.node('C').rect('End');
 *
 * flow.edge('A').to('B').solid();
 * flow.edge('B').to('C').dotted('optional');
 *
 * flow.style.define('highlight', { fill: '#ff0', stroke: '#f00' });
 * flow.style.apply('highlight', 'B');
 *
 * console.log(flow.toString());
 * ```
 *
 * @param options - Diagram options
 * @returns FlowDiagram builder instance
 */
export function FlowDiagram<Nodes extends string = string>(
  options: FlowDiagramOptions = {},
): FlowDiagramBuilder<Nodes> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const store = new DiagramStore(`graph ${opts.direction}`);
  const styleBuilder = createStyleBuilder(store);

  /**
   * Create a subgraph builder that operates within the subgraph context
   */
  const createSubgraphBuilder = (): SubgraphBuilder<Nodes> => ({
    direction(dir: FlowDirection) {
      store.add(`direction ${dir}`);
    },
    node(id: Nodes): NodeBuilder<Nodes> {
      return createNodeBuilder<Nodes>(store, id);
    },
  });

  return {
    node(id: Nodes): NodeBuilder<Nodes> {
      return createNodeBuilder<Nodes>(store, id);
    },

    edge(from: Nodes) {
      return createEdgeBuilder<Nodes>(store, from);
    },

    subgraph(name: string, fn: (sub: SubgraphBuilder<Nodes>) => void) {
      store.add(`subgraph ${name}`);
      store.indent();
      fn(createSubgraphBuilder());
      store.dedent();
      store.add('end');
    },

    style: styleBuilder,

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
