/**
 * Node builder functions for FlowDiagram
 * @module Mermaid/builders/FlowDiagram/functions/getNodes
 */

import { DiagramStore } from '../../core/DiagramStore';
import { NODE_SHAPE_SYNTAX, type NodeShape } from '../../core/types';
import { formatLabel, toNodeId } from '../../core/sanitize';
import type { NodeBuilder } from '../types';

/**
 * Create a node builder for a specific node ID
 */
export function createNodeBuilder<Nodes extends string>(
  store: DiagramStore,
  nodeId: Nodes,
): NodeBuilder<Nodes> {
  const safeId = toNodeId(nodeId);

  const addNode = (shape: NodeShape, label: string, subtitle?: string) => {
    const [open, close] = NODE_SHAPE_SYNTAX[shape];
    const formattedLabel = formatLabel(label, subtitle);

    // Use quoted format for complex labels
    if (subtitle || label.includes(' ') || label.includes(':')) {
      store.add(`${safeId}${open}"${formattedLabel}"${close}`);
    } else {
      store.add(`${safeId}${open}${formattedLabel}${close}`);
    }
  };

  return {
    rect: (label, subtitle) => addNode('rect', label, subtitle),
    round: (label, subtitle) => addNode('round', label, subtitle),
    stadium: (label, subtitle) => addNode('stadium', label, subtitle),
    circle: (label, subtitle) => addNode('circle', label, subtitle),
    rhombus: (label, subtitle) => addNode('rhombus', label, subtitle),
    hexagon: (label, subtitle) => addNode('hexagon', label, subtitle),
    cylinder: (label, subtitle) => addNode('cylinder', label, subtitle),
    subroutine: (label, subtitle) => addNode('subroutine', label, subtitle),
    doubleCircle: (label, subtitle) => addNode('doubleCircle', label, subtitle),
  };
}
