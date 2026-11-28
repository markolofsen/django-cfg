/**
 * Element classification — map a DOM element to a CST node kind & role.
 *
 * The role tables are adapted from cmdop_browser/perception/axtree.py
 * (its `_AX_JS` role map).
 */

import type { CSTContainerRole, CSTInteractiveRole } from '../cst/types';
import { tagName } from './dom-utils';

/** How an element should be represented in the CST. */
export type NodeKind = 'interactive' | 'container' | 'text-host' | 'skip';

/** Tags that are always interactive. */
const INTERACTIVE_TAG_ROLE: Record<string, CSTInteractiveRole> = {
  a: 'link',
  button: 'button',
  select: 'select',
  textarea: 'textarea',
};

/** `<input type>` → interactive role. */
const INPUT_TYPE_ROLE: Record<string, CSTInteractiveRole> = {
  button: 'button',
  submit: 'button',
  reset: 'button',
  checkbox: 'checkbox',
  radio: 'radio',
  range: 'slider',
  number: 'spinbutton',
  search: 'searchbox',
};

/** ARIA roles we treat as interactive. */
const ARIA_INTERACTIVE: ReadonlySet<string> = new Set([
  'button',
  'link',
  'textbox',
  'checkbox',
  'radio',
  'combobox',
  'switch',
  'tab',
  'menuitem',
  'slider',
  'spinbutton',
  'searchbox',
]);

/**
 * Tag → container role.
 *
 * `tr` / `li` map to `section` so each row / list item stays its own
 * node — this is what lets sibling folding collapse repetitive table
 * rows and list items (see fold.ts). Without it the cells
 * flatten into one undifferentiated list and folding cannot fire.
 */
const CONTAINER_TAG_ROLE: Record<string, CSTContainerRole> = {
  form: 'form',
  table: 'table',
  thead: 'section',
  tbody: 'section',
  tr: 'section',
  ul: 'list',
  ol: 'list',
  li: 'section',
  nav: 'navigation',
  section: 'section',
  article: 'section',
};

/** ARIA role → container role. */
const ARIA_CONTAINER: Record<string, CSTContainerRole> = {
  form: 'form',
  table: 'table',
  grid: 'grid',
  list: 'list',
  navigation: 'navigation',
  region: 'region',
};

/** Resolve the interactive role of an element, if it is interactive. */
export function interactiveRole(el: Element): CSTInteractiveRole | null {
  const aria = el.getAttribute('role')?.toLowerCase();
  if (aria && ARIA_INTERACTIVE.has(aria)) {
    return aria as CSTInteractiveRole;
  }

  const tag = tagName(el);
  if (tag === 'input') {
    const type = (el.getAttribute('type') ?? 'text').toLowerCase();
    return INPUT_TYPE_ROLE[type] ?? 'textbox';
  }
  if (el.getAttribute('contenteditable') === 'true') return 'textbox';

  return INTERACTIVE_TAG_ROLE[tag] ?? null;
}

/** Resolve the container role of an element, if it is a container. */
export function containerRole(el: Element): CSTContainerRole | null {
  const aria = el.getAttribute('role')?.toLowerCase();
  const ariaRole = aria ? ARIA_CONTAINER[aria] : undefined;
  if (ariaRole) return ariaRole;
  return CONTAINER_TAG_ROLE[tagName(el)] ?? null;
}

/** Classify an element into a CST node kind. */
export function classify(el: Element): NodeKind {
  if (interactiveRole(el)) return 'interactive';
  if (containerRole(el)) return 'container';
  return 'text-host';
}
