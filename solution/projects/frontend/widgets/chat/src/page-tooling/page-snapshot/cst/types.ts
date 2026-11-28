/**
 * Compact Semantic Tree (CST) — the snapshot representation.
 *
 * A token-efficient typed tree of a rendered page: interactive elements
 * carry short stable ref ids, containers give structure, prose collapses
 * into Markdown text nodes. ~90–95% smaller than raw HTML.
 *
 */

/** Short stable ref of an interactive CST node, e.g. "@e4". */
export type CSTRefId = `@e${number}`;

/** Roles an interactive node can take. */
export type CSTInteractiveRole =
  | 'button'
  | 'link'
  | 'textbox'
  | 'checkbox'
  | 'radio'
  | 'combobox'
  | 'select'
  | 'textarea'
  | 'slider'
  | 'spinbutton'
  | 'searchbox'
  | 'switch'
  | 'tab'
  | 'menuitem'
  | 'dialog';

/** Roles a container node can take. */
export type CSTContainerRole =
  | 'form'
  | 'table'
  | 'list'
  | 'section'
  | 'grid'
  | 'navigation'
  | 'region';

/** Discriminated union of every CST node kind. */
export type CSTNode =
  | CSTRootNode
  | CSTInteractiveNode
  | CSTContainerNode
  | CSTTextNode;

/** Root of a snapshot tree. */
export interface CSTRootNode {
  type: 'root';
  /** Page title (document.title). */
  title: string;
  /** Page URL at capture time. */
  url: string;
  children: CSTNode[];
}

/**
 * An interactive element — button, input, select, etc.
 * The `ref` is the address the AI uses to point at it later.
 */
export interface CSTInteractiveNode {
  type: 'interactive';
  role: CSTInteractiveRole;
  /** Stable ref id, unique within the snapshot. */
  ref: CSTRefId;
  /** Accessible name. */
  name: string;
  /** Current value, if any (already redaction-processed). */
  value?: string;
  /** Placeholder text, if any. */
  placeholder?: string;
  disabled?: boolean;
  checked?: boolean;
  expanded?: boolean;
  required?: boolean;
}

/** A structural grouping — form, table, section, etc. */
export interface CSTContainerNode {
  type: 'container';
  role: CSTContainerRole;
  /** Optional accessible name / heading. */
  name?: string;
  children: CSTNode[];
}

/** A run of static prose, collapsed into compact Markdown. */
export interface CSTTextNode {
  type: 'text';
  /** Pruned structural text formatted as simplified Markdown. */
  content: string;
}

/** Type guard: is this an interactive node. */
export function isInteractiveNode(node: CSTNode): node is CSTInteractiveNode {
  return node.type === 'interactive';
}

/** Type guard: is this a container node. */
export function isContainerNode(node: CSTNode): node is CSTContainerNode {
  return node.type === 'container';
}

/** Type guard: is this a text node. */
export function isTextNode(node: CSTNode): node is CSTTextNode {
  return node.type === 'text';
}

/** Nodes that can have children. */
export function hasChildren(
  node: CSTNode,
): node is CSTRootNode | CSTContainerNode {
  return node.type === 'root' || node.type === 'container';
}
