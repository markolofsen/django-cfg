/**
 * Scope detection — find the root element(s) the DOM walk starts from.
 *
 * Implements the 6-tier fallback ladder: try each tier
 * top-to-bottom, first non-empty result wins. `[data-ai-context]` is an
 * optional refinement (Tier 1), NOT a requirement — auto-detection
 * works on un-annotated pages.
 *
 */

import { isChrome } from "./chrome-filter";
import { elementArea, isVisible, linkDensity } from "./dom-utils";

/** Strategy for choosing the capture root. */
export type ScopeStrategy = "container" | "viewport" | "full";

/** Options influencing scope resolution. */
export interface ScopeOptions {
  strategy: ScopeStrategy;
  /** Optional explicit selector; overrides auto-detection entirely. */
  targetSelector?: string;
}

/** Which tier produced the resolved scope (for telemetry / debugging). */
export type ScopeTier =
  | "explicit-selector"
  | "tier0-dialog"
  | "tier1-annotation"
  | "tier2-main"
  | "tier3-heuristic"
  | "tier4-body"
  | "tier5-viewport";

/** Resolved capture scope. */
export interface ResolvedScope {
  /** Root element(s) to walk. Usually one; dialogs/multi-panel give more. */
  roots: HTMLElement[];
  /** The tier that produced this result. */
  tier: ScopeTier;
}

/** Block-level tags considered as heuristic content candidates (Tier 3). */
const CANDIDATE_SELECTOR = 'div, section, article, form, table, ul, ol, [role="region"]';

/** Anything whose presence makes a block worth walking (Tier 3). */
const CONTENT_SELECTOR =
  "a, button, input, select, textarea, img, h1, h2, h3, h4, h5, h6, p, li, td, [role]";

/** Tier 0 — a visible open modal / dialog overrides everything. */
function tierDialog(): HTMLElement | null {
  const selectors = [
    '[role="dialog"][aria-modal="true"]',
    '[role="alertdialog"][aria-modal="true"]',
    "dialog[open]",
  ];
  for (const sel of selectors) {
    const nodes = Array.from(document.querySelectorAll(sel));
    const visible = nodes.filter((n) => isVisible(n)) as HTMLElement[];
    if (visible.length > 0) {
      // Topmost / largest open dialog.
      return visible.sort((a, b) => elementArea(b) - elementArea(a))[0] ?? null;
    }
  }
  return null;
}

/** Tier 1 — explicit `[data-ai-context]` annotation (optional refinement). */
function tierAnnotation(): HTMLElement[] {
  const nodes = Array.from(document.querySelectorAll("[data-ai-context]")) as HTMLElement[];
  return nodes.filter((n) => isVisible(n) && n.dataset.aiContext !== "exclude");
}

/** Tier 2 — ARIA `<main>` / `role="main"`. */
function tierMain(): HTMLElement | null {
  const nodes = Array.from(document.querySelectorAll('main, [role="main"]')) as HTMLElement[];
  const visible = nodes.filter((n) => isVisible(n));
  if (visible.length === 0) return null;
  if (visible.length === 1) return visible[0] ?? null;
  // Multiple — take the largest by rendered area.
  return visible.sort((a, b) => elementArea(b) - elementArea(a))[0] ?? null;
}

/**
 * Does this block hold anything worth capturing?
 *
 * Cheap and structural on purpose: the walk decides what is actually
 * interesting, this only rejects candidates that would give it nothing.
 */
function hasContent(el: HTMLElement): boolean {
  if (el.querySelector(CONTENT_SELECTOR) !== null) return true;
  return (el.textContent ?? "").trim().length > 0;
}

/** Tier 3 — heuristic largest non-chrome content block. */
function tierHeuristic(): HTMLElement | null {
  const docArea = Math.max(
    1,
    document.documentElement.clientWidth * document.documentElement.clientHeight
  );
  const candidates = Array.from(
    document.body.querySelectorAll(CANDIDATE_SELECTOR)
  ) as HTMLElement[];

  let best: HTMLElement | null = null;
  let bestScore = 0;

  for (const el of candidates) {
    if (!isVisible(el) || isChrome(el)) continue;
    const normalizedArea = Math.min(1, elementArea(el) / docArea);
    if (normalizedArea < 0.05) continue; // too small to be main content
    // Area alone ranks an empty full-viewport overlay — a toast layer, a glow
    // border, a portal root — above the content it covers, and the walk then
    // visits one node and returns a tree with no children. Nothing errors:
    // the snapshot is simply empty, and the assistant is told the page has
    // nothing on it.
    if (!hasContent(el)) continue;
    const density = linkDensity(el);
    // Favor large, low-link-density blocks (boilerplate is link-dense).
    const score = normalizedArea * (1 - density);
    // `>` keeps the FIRST of equal scores, and two wrappers around the same
    // content tie exactly. First in document order is the outer one, which
    // still contains the content — so the tie is safe once empties are out.
    if (score > bestScore) {
      bestScore = score;
      best = el;
    }
  }
  return best;
}

/**
 * Tier 5 — intersect a root with the viewport. Last resort for huge
 * pages: returns the root itself (the walk's own viewport filtering
 * trims off-screen nodes).
 */
function tierViewport(root: HTMLElement): HTMLElement {
  return root;
}

/**
 * Resolve the scope to walk.
 *
 * Honors an explicit `targetSelector` first; otherwise runs the ladder.
 * The `strategy` option biases the ladder: `'viewport'` jumps to the
 * viewport tier, `'full'` forces body-minus-chrome.
 */
export function resolveScope(options: ScopeOptions): ResolvedScope {
  if (typeof document === "undefined") {
    throw new Error("resolveScope: no document (non-browser runtime).");
  }

  // Explicit selector — caller knows best.
  if (options.targetSelector) {
    const el = document.querySelector(options.targetSelector);
    if (el instanceof HTMLElement) {
      return { roots: [el], tier: "explicit-selector" };
    }
  }

  // Strategy shortcuts.
  if (options.strategy === "full") {
    return { roots: [document.body], tier: "tier4-body" };
  }
  if (options.strategy === "viewport") {
    return { roots: [tierViewport(document.body)], tier: "tier5-viewport" };
  }

  // The ladder (strategy === 'container').
  const dialog = tierDialog();
  if (dialog) return { roots: [dialog], tier: "tier0-dialog" };

  const annotated = tierAnnotation();
  if (annotated.length > 0) {
    return { roots: annotated, tier: "tier1-annotation" };
  }

  const main = tierMain();
  if (main) return { roots: [main], tier: "tier2-main" };

  const heuristic = tierHeuristic();
  if (heuristic) return { roots: [heuristic], tier: "tier3-heuristic" };

  // Tier 4 — body minus chrome (chrome is filtered during the walk).
  return { roots: [document.body], tier: "tier4-body" };
}
