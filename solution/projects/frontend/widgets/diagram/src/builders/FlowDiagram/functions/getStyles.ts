/**
 * Style builder functions for FlowDiagram
 * @module Mermaid/builders/FlowDiagram/functions/getStyles
 */

import { DiagramStore } from '../../core/DiagramStore';
import type { StyleProperties } from '../../core/types';
import { toNodeId } from '../../core/sanitize';
import type { StyleBuilder } from '../types';

/**
 * Convert style properties to Mermaid classDef syntax
 */
function propertiesToString(properties: StyleProperties): string {
  const parts: string[] = [];

  if (properties.fill) parts.push(`fill:${properties.fill}`);
  if (properties.stroke) parts.push(`stroke:${properties.stroke}`);
  if (properties['stroke-width']) parts.push(`stroke-width:${properties['stroke-width']}`);
  if (properties.color) parts.push(`color:${properties.color}`);
  if (properties['font-weight']) parts.push(`font-weight:${properties['font-weight']}`);
  if (properties['stroke-dasharray']) parts.push(`stroke-dasharray:${properties['stroke-dasharray']}`);

  return parts.join(',');
}

/**
 * Create a style builder
 */
export function createStyleBuilder(store: DiagramStore): StyleBuilder {
  return {
    define(name: string, properties: StyleProperties): void {
      const propsStr = propertiesToString(properties);
      store.add(`classDef ${name} ${propsStr}`);
    },

    apply(className: string, ...nodeIds: string[]): void {
      if (nodeIds.length === 0) return;
      const safeIds = nodeIds.map((id) => toNodeId(id)).join(',');
      store.add(`class ${safeIds} ${className}`);
    },
  };
}

// ============================================================================
// Predefined Style Classes (Common patterns)
// ============================================================================

/**
 * Common style presets for quick use
 */
export const STYLE_PRESETS = {
  /** Green success style */
  success: {
    fill: '#22c55e',
    stroke: '#16a34a',
    color: '#fff',
  },
  /** Blue primary style */
  primary: {
    fill: '#3b82f6',
    stroke: '#1d4ed8',
    color: '#fff',
  },
  /** Red error/danger style */
  danger: {
    fill: '#ef4444',
    stroke: '#dc2626',
    color: '#fff',
  },
  /** Yellow warning style */
  warning: {
    fill: '#f59e0b',
    stroke: '#d97706',
    color: '#fff',
  },
  /** Gray muted style */
  muted: {
    fill: '#6b7280',
    stroke: '#4b5563',
    color: '#fff',
  },
  /** Emerald/teal accent */
  accent: {
    fill: '#10b981',
    stroke: '#047857',
    color: '#fff',
    'font-weight': 'bold' as const,
  },
} satisfies Record<string, StyleProperties>;
