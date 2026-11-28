/**
 * Types for FlowDiagram builder
 * @module Mermaid/builders/FlowDiagram/types
 */

import type { FlowDirection, NodeShape, StyleProperties } from '../core/types';

/**
 * Options for FlowDiagram builder
 */
export interface FlowDiagramOptions {
  /** Diagram direction (default: 'TB') */
  direction?: FlowDirection;
}

/**
 * Node definition
 */
export interface NodeDefinition {
  id: string;
  label: string;
  shape: NodeShape;
  subtitle?: string;
}

/**
 * Edge definition
 */
export interface EdgeDefinition {
  from: string;
  to: string;
  label?: string;
  style: 'solid' | 'dotted' | 'thick';
}

/**
 * Style class definition for flow diagrams
 */
export interface FlowStyleClass {
  name: string;
  properties: StyleProperties;
}

/**
 * Node builder interface - chainable API for creating nodes
 *
 * `Nodes` is phantom here — every method returns `void` — but it is kept so the
 * builder family reads uniformly (`node(id: Nodes): NodeBuilder<Nodes>`) and so
 * the exported type stays source-compatible for callers that write it out.
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export interface NodeBuilder<Nodes extends string> {
  /** Create a rectangular node [label] */
  rect(label: string, subtitle?: string): void;
  /** Create a rounded node (label) */
  round(label: string, subtitle?: string): void;
  /** Create a stadium/pill node ([label]) */
  stadium(label: string, subtitle?: string): void;
  /** Create a circular node ((label)) */
  circle(label: string, subtitle?: string): void;
  /** Create a rhombus/diamond node {label} */
  rhombus(label: string, subtitle?: string): void;
  /** Create a hexagon node {{label}} */
  hexagon(label: string, subtitle?: string): void;
  /** Create a cylinder/database node [(label)] */
  cylinder(label: string, subtitle?: string): void;
  /** Create a subroutine node [[label]] */
  subroutine(label: string, subtitle?: string): void;
  /** Create a double circle node (((label))) */
  doubleCircle(label: string, subtitle?: string): void;
}

/**
 * Edge builder interface - chainable API for creating edges
 */
export interface EdgeBuilder<Nodes extends string> {
  /** Target node for the edge */
  to(target: Nodes): EdgeEndBuilder;
}

/**
 * Edge end builder - configures the edge after target is specified
 */
export interface EdgeEndBuilder {
  /** Solid arrow --> */
  solid(label?: string): void;
  /** Dotted arrow -.-> */
  dotted(label?: string): void;
  /** Thick arrow ==> */
  thick(label?: string): void;
  /** Solid line without arrow --- */
  line(label?: string): void;
  /** Dotted line without arrow -.- */
  dottedLine(label?: string): void;
}

/**
 * Style builder interface
 */
export interface StyleBuilder {
  /** Define a style class */
  define(name: string, properties: StyleProperties): void;
  /** Apply a class to nodes */
  apply(className: string, ...nodeIds: string[]): void;
}

/**
 * Subgraph builder interface
 */
export interface SubgraphBuilder<Nodes extends string> {
  /** Set direction inside subgraph */
  direction(dir: FlowDirection): void;
  /** Create a node inside subgraph */
  node(id: Nodes): NodeBuilder<Nodes>;
}

/**
 * Main FlowDiagram builder result
 */
export interface FlowDiagramBuilder<Nodes extends string> {
  /** Create a node */
  node: (id: Nodes) => NodeBuilder<Nodes>;
  /** Create an edge from a node */
  edge: (from: Nodes) => EdgeBuilder<Nodes>;
  /** Create a subgraph */
  subgraph: (name: string, fn: (sub: SubgraphBuilder<Nodes>) => void) => void;
  /** Style utilities */
  style: StyleBuilder;
  /** Add a comment */
  comment: (text: string) => void;
  /** Add a blank line */
  blank: () => void;
  /** Get the Mermaid string */
  toString: () => string;
}
