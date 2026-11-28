/**
 * DOM → CST walker.
 *
 * Recursively walks a scope root into CST nodes: visibility filtering,
 * chrome exclusion, role classification, ref assignment, and a
 * redaction hook for every captured value/text.
 *
 * Layout reads are confined to dom-utils helpers; the walk itself does
 * no interleaved geometry queries beyond the up-front visibility check.
 *
 */

import type {
  CSTContainerNode,
  CSTInteractiveNode,
  CSTNode,
  CSTRefId,
  CSTTextNode,
} from '../cst/types';
import { computeLocator, type RefLocator } from '../refs/locator';
import { accessibleName } from './accessible-name';
import {
  classify,
  containerRole,
  interactiveRole,
} from './classify';
import { isChrome } from './chrome-filter';
import {
  PLACEHOLDER_TAGS,
  SKIP_TAGS,
  isVisible,
  tagName,
} from './dom-utils';

/** A value passed through redaction before entering the tree. */
export type RedactValue = (value: string, context: RedactContext) => string;

/** Context for a redaction decision. */
export interface RedactContext {
  /** Element the value came from. */
  element: HTMLElement;
  /** Where the value sits — an input value or static text. */
  kind: 'value' | 'text';
  /** Ref id assigned to the element, if any. */
  ref?: CSTRefId;
}

/** No-op redaction — passes values through unchanged. */
export const noopRedact: RedactValue = (value) => value;

/** Result of walking the DOM under a scope root. */
export interface WalkResult {
  /** Captured child nodes (the root node is assembled by the engine). */
  children: CSTNode[];
  /**
   * Map of assigned ref id → re-locatable descriptor. A descriptor —
   * not a node pointer — because React recreates DOM nodes between
   * capture and directive application; a frozen `HTMLElement` would be
   * detached by then. The descriptor re-finds the element in the live
   * DOM at resolve time.
   */
  refMap: Map<CSTRefId, RefLocator>;
  /** First unused ref number — the next root's `startRef`. */
  nextRef: number;
  /** Number of elements visited. */
  nodesVisited: number;
}

/** Options for a walk. */
export interface WalkOptions {
  /** Redaction hook; defaults to no-op. */
  redactValue?: RedactValue;
  /** Hard cap on elements visited (safety valve); default 50_000. */
  maxNodes?: number;
  /**
   * First ref number to assign; defaults to 1.
   *
   * A scope can have several roots (Tier 1 returns every visible
   * `[data-ai-context]`), and one snapshot's refs must be unique across all of
   * them — the caller merges the maps into a single registry. Restarting at 1
   * per root makes the second root's `@e1` overwrite the first's, so the ref
   * resolves to the wrong element rather than to nothing.
   */
  startRef?: number;
}

/** Mutable state threaded through one walk. */
interface WalkState {
  redact: RedactValue;
  refMap: Map<CSTRefId, RefLocator>;
  refCounter: number;
  visited: number;
  maxNodes: number;
}

/** Minimum trimmed length for a text node to be worth keeping. */
const MIN_TEXT_LEN = 2;

/** Read the current value of a form control as a string. */
function controlValue(el: Element): string | undefined {
  if (el instanceof HTMLInputElement) {
    if (el.type === 'checkbox' || el.type === 'radio') return undefined;
    return el.value || undefined;
  }
  if (el instanceof HTMLTextAreaElement) return el.value || undefined;
  if (el instanceof HTMLSelectElement) {
    return el.selectedOptions[0]?.textContent?.trim() || undefined;
  }
  if (el.getAttribute('contenteditable') === 'true') {
    return el.textContent?.trim() || undefined;
  }
  return undefined;
}

/** Build an interactive CST node for an element. */
function buildInteractive(el: HTMLElement, state: WalkState): CSTInteractiveNode {
  const role = interactiveRole(el)!;
  const ref = `@e${state.refCounter++}` as CSTRefId;
  // Store a re-locatable descriptor, never the node itself — the node
  // will be recreated by React before the directive arrives.
  state.refMap.set(ref, computeLocator(el, role));

  const rawValue = controlValue(el);
  const value =
    rawValue === undefined
      ? undefined
      : state.redact(rawValue, { element: el, kind: 'value', ref });

  const node: CSTInteractiveNode = {
    type: 'interactive',
    role,
    ref,
    name: accessibleName(el),
  };
  if (value !== undefined) node.value = value;

  const placeholder = el.getAttribute('placeholder');
  if (placeholder) node.placeholder = placeholder;

  if (el instanceof HTMLInputElement) {
    if (el.type === 'checkbox' || el.type === 'radio') {
      node.checked = el.checked;
    }
  }
  const ariaChecked = el.getAttribute('aria-checked');
  if (ariaChecked === 'true' || ariaChecked === 'false') {
    node.checked = ariaChecked === 'true';
  }
  const ariaExpanded = el.getAttribute('aria-expanded');
  if (ariaExpanded === 'true' || ariaExpanded === 'false') {
    node.expanded = ariaExpanded === 'true';
  }
  if (
    'disabled' in el &&
    (el as HTMLInputElement).disabled === true
  ) {
    node.disabled = true;
  }
  if (el.getAttribute('aria-disabled') === 'true') node.disabled = true;
  if (
    el.getAttribute('required') !== null ||
    el.getAttribute('aria-required') === 'true'
  ) {
    node.required = true;
  }

  return node;
}

/** Collect direct-child text not owned by a child element. */
function ownText(el: Element, state: WalkState): string {
  let text = '';
  el.childNodes.forEach((n) => {
    if (n.nodeType === 3 /* TEXT_NODE */) {
      text += n.textContent ?? '';
    }
  });
  const trimmed = text.replace(/\s+/g, ' ').trim();
  if (trimmed.length < MIN_TEXT_LEN) return '';
  return state.redact(trimmed, {
    element: el as HTMLElement,
    kind: 'text',
  });
}

/** Walk one element into zero or more CST nodes. */
function walkElement(el: Element, state: WalkState): CSTNode[] {
  if (state.visited >= state.maxNodes) return [];
  state.visited++;

  const tag = tagName(el);
  if (SKIP_TAGS.has(tag)) return [];
  if (!(el instanceof HTMLElement)) return [];
  if (isChrome(el)) return [];
  if (!isVisible(el)) return [];

  // data-ai-redact — drop the whole subtree, replace with a placeholder.
  // Checked on the element itself; the walk descends top-down so an
  // annotated ancestor is caught before any descendant is reached.
  if (el.hasAttribute('data-ai-redact')) {
    return [{ type: 'text', content: '[redacted]' } satisfies CSTTextNode];
  }

  // Canvas / SVG / iframe — placeholder, no descent (also redaction-safe).
  if (PLACEHOLDER_TAGS.has(tag)) {
    const label = accessibleName(el) || tag;
    return [{ type: 'text', content: `[${label}]` } satisfies CSTTextNode];
  }

  const kind = classify(el);

  if (kind === 'interactive') {
    return [buildInteractive(el, state)];
  }

  // Container or text-host: gather children, plus own text.
  const childNodes: CSTNode[] = [];
  const text = ownText(el, state);
  if (text) childNodes.push({ type: 'text', content: text });
  for (const child of Array.from(el.children)) {
    childNodes.push(...walkElement(child, state));
  }

  if (childNodes.length === 0) return [];

  if (kind === 'container') {
    const node: CSTContainerNode = {
      type: 'container',
      role: containerRole(el)!,
      children: childNodes,
    };
    const name = accessibleName(el);
    if (name && name.length <= 80) node.name = name;
    return [node];
  }

  // text-host: a plain wrapper — flatten, don't add a tree level.
  return childNodes;
}

/**
 * Walk the DOM subtree under `root` into CST child nodes.
 */
export function walkDOM(
  root: HTMLElement,
  options: WalkOptions = {},
): WalkResult {
  const state: WalkState = {
    redact: options.redactValue ?? noopRedact,
    refMap: new Map(),
    refCounter: options.startRef ?? 1,
    visited: 0,
    maxNodes: options.maxNodes ?? 50_000,
  };

  // Walk the root's children — the root element itself becomes the CST
  // root node, assembled by the engine.
  const children: CSTNode[] = [];
  const text = ownText(root, state);
  if (text) children.push({ type: 'text', content: text });
  for (const child of Array.from(root.children)) {
    children.push(...walkElement(child, state));
  }

  return {
    children,
    refMap: state.refMap,
    nextRef: state.refCounter,
    nodesVisited: state.visited,
  };
}
