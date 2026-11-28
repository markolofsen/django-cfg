/**
 * Re-locatable ref descriptors.
 *
 * A snapshot is captured when a chat message is sent; the AI's
 * `point` directive arrives seconds later. In between, React re-renders
 * the page — the chat panel expands, content streams in, lists update —
 * and React recreates DOM nodes. Any `HTMLElement` reference frozen at
 * capture time is then detached (`isConnected === false`) and useless.
 *
 * So a ref must NOT be stored as a node pointer. It is stored as a
 * `RefLocator`: a description rich enough to FIND the element again in
 * whatever DOM exists at resolve time. `resolveLocator` runs a live
 * query against the current `document` — it never dereferences a stale
 * pointer.
 */

import { accessibleName } from '../capture/accessible-name';
import { tagName } from '../capture/dom-utils';
import type { CSTInteractiveRole } from '../cst/types';

/**
 * A description that can re-find an interactive element in the live DOM.
 *
 * `role` + `name` is the primary locator: the AI cited an element by the
 * accessible name the CST gave it, so "the visible `link` named 'Browse
 * Catalog'" survives node-identity changes and even position shifts.
 * `selector` is a structural tiebreaker used to disambiguate when
 * several elements share the same role + name.
 */
export interface RefLocator {
  /** Interactive role, as classified by the CST walk. */
  role: CSTInteractiveRole;
  /** Accessible name — the label the AI was shown for this element. */
  name: string;
  /** lowercased tag name, used to filter candidates. */
  tag: string;
  /**
   * A CSS selector that re-finds the element. Built from a stable
   * attribute (`id` / `data-testid` / `name`) when one exists, else a
   * structural `nth-of-type` path from the nearest id'd ancestor or
   * `<body>`. A tiebreaker, not the source of truth — React can
   * recreate nodes and shift positions, breaking the path.
   */
  selector: string;
  /**
   * Whether `selector` came from a stable attribute rather than position.
   *
   * The two are not interchangeable and `resolveLocator` must not treat them
   * alike. An attribute selector names the element; a positional one names a
   * SLOT, and after a sibling is removed that slot holds a different element —
   * still exactly one match, so a hit count cannot tell them apart.
   */
  stable: boolean;
  /**
   * Text of the nearest ancestor that tells this element apart from its
   * same-named peers — a table row's cells, a card's heading.
   *
   * A row's Delete button is named "Delete" in every row, so `name` alone
   * cannot pick one and position picks a slot. The CST already gives the model
   * this context (the row's own text sits beside the button), and it is what
   * the model means by "delete Beta". Empty when the name is unambiguous.
   */
  context?: string;
}

/** Attributes that, when present, give a stable unique-ish selector. */
const STABLE_ATTRS = ['data-testid', 'id', 'name'] as const;

/** True when a selector matches exactly one element in `document`. */
function isUnique(selector: string): boolean {
  try {
    return document.querySelectorAll(selector).length === 1;
  } catch {
    return false;
  }
}

/** Escape a value for use inside a CSS attribute selector. */
function cssEscape(value: string): string {
  if (typeof CSS !== 'undefined' && typeof CSS.escape === 'function') {
    return CSS.escape(value);
  }
  return value.replace(/[^a-zA-Z0-9_-]/g, (ch) => `\\${ch}`);
}

/**
 * Build a structural `nth-of-type` path from the nearest id'd ancestor
 * (or `<body>`) down to `el`. Survives re-renders that recreate nodes
 * but keep the same tag structure and ordering — the common React case.
 */
function structuralPath(el: HTMLElement): string {
  const parts: string[] = [];
  let node: Element | null = el;
  while (node && node !== document.body && node !== document.documentElement) {
    const id = node.getAttribute('id');
    if (id) {
      parts.unshift(`#${cssEscape(id)}`);
      return parts.join(' > ');
    }
    const tag = tagName(node);
    const parent: Element | null = node.parentElement;
    if (!parent) {
      parts.unshift(tag);
      break;
    }
    let index = 1;
    for (const sib of Array.from(parent.children)) {
      if (sib === node) break;
      if (tagName(sib) === tag) index += 1;
    }
    parts.unshift(`${tag}:nth-of-type(${index})`);
    node = parent;
  }
  return parts.length ? `body > ${parts.join(' > ')}` : 'body';
}

/**
 * Compute a re-locatable descriptor for an interactive element at
 * capture time. `role` is already known from classification; `name` is
 * derived with the same accessible-name logic the CST walk uses, so the
 * locator's name matches exactly what the AI was shown.
 */
export function computeLocator(
  el: HTMLElement,
  role: CSTInteractiveRole,
): RefLocator {
  let selector = '';
  for (const attr of STABLE_ATTRS) {
    const raw = el.getAttribute(attr);
    if (!raw) continue;
    const candidate =
      attr === 'id'
        ? `#${cssEscape(raw)}`
        : `${tagName(el)}[${attr}="${cssEscape(raw)}"]`;
    if (isUnique(candidate)) {
      selector = candidate;
      break;
    }
  }
  const stable = selector !== '';
  if (!stable) selector = structuralPath(el);

  const name = accessibleName(el);
  const context = stable ? '' : disambiguatingContext(el, role, name);

  return {
    role,
    name,
    tag: tagName(el),
    selector,
    stable,
    ...(context ? { context } : {}),
  };
}

/**
 * Text of the nearest ancestor that separates `el` from its same-named peers.
 *
 * Climbs one level at a time and stops at the first ancestor whose text no
 * peer's ancestor at the SAME depth shares — the table row, not the table.
 * Returns '' when the name is already unique: context nobody needs only makes
 * a working locator brittle.
 */
function disambiguatingContext(
  el: HTMLElement,
  role: CSTInteractiveRole,
  name: string,
): string {
  const peers = collectByRoleName({
    role,
    name,
    tag: tagName(el),
    selector: '',
    stable: false,
  }).filter((peer) => peer !== el);
  if (peers.length === 0) return '';

  // Bounded: a row or card sits a few levels up, and beyond that the ancestor
  // is shared with the peers, so climbing further cannot separate them.
  let node: HTMLElement | null = el.parentElement;
  for (let depth = 1; node && depth <= 4; depth += 1) {
    const text = textOf(node);
    if (text && peers.every((peer) => textOf(ancestorAt(peer, depth)) !== text)) {
      return text;
    }
    node = node.parentElement;
  }
  return '';
}

/** The ancestor `depth` levels above `el`, or null. */
function ancestorAt(el: HTMLElement, depth: number): HTMLElement | null {
  let node: HTMLElement | null = el;
  for (let i = 0; i < depth && node; i += 1) node = node.parentElement;
  return node;
}

/** Visible text of an element, normalised the way names are. */
function textOf(el: Element | null): string {
  if (!el) return '';
  return (el.textContent ?? '').replace(/\s+/g, ' ').trim().slice(0, 120);
}

/** True when an element is rendered (has layout) — prefers visible hits. */
function isRendered(el: HTMLElement): boolean {
  if (!el.isConnected) return false;
  // offsetParent is null for display:none; width/height covers fixed
  // and body-level elements that legitimately have no offsetParent.
  return (
    el.offsetParent !== null ||
    el.getClientRects().length > 0
  );
}

/**
 * Find a connected element matching a locator against the live DOM.
 *
 * Resolution order:
 *  1. a STABLE attribute selector (`id` / `data-testid` / `name`) — it names
 *     the element, so a single hit is the element;
 *  2. role + accessible name, with the positional selector used only to
 *     choose among several matches. Identity comes from what the element IS,
 *     never from where it sits;
 *  3. give up — the element is genuinely gone (stale ref).
 *
 * A positional selector is deliberately NOT trusted on its own. It names a
 * slot, not an element: delete a table row and `tr:nth-of-type(2) > … > button`
 * still matches exactly one button — the next row's. Three refs into a
 * three-row table resolved to Beta, Gamma and Beta after the first row was
 * removed, with no error anywhere. A hit count cannot detect that; only
 * checking the name can.
 */
export function resolveLocator(locator: RefLocator): HTMLElement | null {
  // 1. A stable attribute names the element itself.
  if (locator.stable) {
    try {
      const hits = document.querySelectorAll<HTMLElement>(locator.selector);
      const only = hits.length === 1 ? hits[0] : undefined;
      if (only?.isConnected) return only;
    } catch {
      // Malformed selector — fall through to the role+name match.
    }
  }

  // 2. Role + accessible name — robust to node recreation AND to a shift.
  const candidates = collectByRoleName(locator);
  if (candidates.length === 0) return null;
  if (candidates.length === 1) return candidates[0] ?? null;

  // Several elements answer to the same name. Context first: it is what the
  // model itself used to tell them apart — the row's own text sits beside the
  // button in the CST — and unlike position it survives a sibling leaving.
  if (locator.context) {
    // A locator that needed context to be unique must still answer to it.
    // Nothing carrying it means the element this ref named is gone — the row
    // was deleted — and the honest answer is null. Falling through to position
    // here is what returned a live sibling for a deleted row.
    return matchByContext(locator, candidates);
  }

  // No context was needed at capture time, so position among elements already
  // correct by name is the tiebreaker. Never an answer on its own.
  const positional = matchBySelector(locator, candidates);
  if (positional) return positional;

  return candidates.find(isRendered) ?? candidates[0] ?? null;
}

/** The one candidate whose surroundings still read as the captured context. */
function matchByContext(
  locator: RefLocator,
  candidates: HTMLElement[],
): HTMLElement | null {
  const wanted = locator.context;
  if (!wanted) return null;
  const matched = candidates.filter((el) => hasContext(el, wanted));
  return matched.length === 1 ? (matched[0] ?? null) : null;
}

/** Whether any ancestor within reach carries exactly this text. */
function hasContext(el: HTMLElement, wanted: string): boolean {
  let node: HTMLElement | null = el.parentElement;
  // The same bound `disambiguatingContext` climbs, for the same reason.
  for (let depth = 1; node && depth <= 4; depth += 1) {
    if (textOf(node) === wanted) return true;
    node = node.parentElement;
  }
  return false;
}

/** The candidate the locator's selector points at, when it points at one. */
function matchBySelector(
  locator: RefLocator,
  candidates: HTMLElement[],
): HTMLElement | null {
  try {
    const hits = new Set(
      document.querySelectorAll<HTMLElement>(locator.selector),
    );
    const matched = candidates.filter((el) => hits.has(el));
    return matched.length === 1 ? (matched[0] ?? null) : null;
  } catch {
    return null;
  }
}

/** Tags worth scanning for a given role when matching by role + name. */
function tagsForRole(role: CSTInteractiveRole): string[] {
  switch (role) {
    case 'link':
      return ['a'];
    case 'button':
      return ['button', 'a', 'input'];
    case 'textbox':
    case 'searchbox':
      return ['input', 'textarea'];
    case 'checkbox':
    case 'radio':
    case 'slider':
    case 'spinbutton':
      return ['input'];
    case 'select':
    case 'combobox':
      return ['select'];
    case 'textarea':
      return ['textarea'];
    default:
      return ['button', 'a', 'input'];
  }
}

/**
 * Collect connected elements whose role + accessible name match the
 * locator. Also scans `[role=...]` so ARIA-roled elements are found.
 */
function collectByRoleName(locator: RefLocator): HTMLElement[] {
  const seen = new Set<HTMLElement>();
  const selectors = [
    ...tagsForRole(locator.role),
    `[role="${locator.role}"]`,
  ];
  const out: HTMLElement[] = [];
  for (const sel of selectors) {
    let nodes: NodeListOf<HTMLElement>;
    try {
      nodes = document.querySelectorAll<HTMLElement>(sel);
    } catch {
      continue;
    }
    for (const node of Array.from(nodes)) {
      if (seen.has(node) || !node.isConnected) continue;
      seen.add(node);
      if (accessibleName(node) === locator.name) out.push(node);
    }
  }
  return out;
}
