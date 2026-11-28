/**
 * Token-budget enforcement — degradation ladder.
 *
 * Sibling folding (fold.ts) runs first and always. If the snapshot is
 * still over budget, this applies progressive degradation:
 *   1. truncate long text nodes
 *   2. drop static text, keep only interactive skeleton
 *
 */

import type { CSTNode } from '../cst/types';
import { hasChildren, isTextNode } from '../cst/types';
import { serializeCST } from '../cst/serialize';
import { estimateTokens } from '../tokens';

/** Max characters a text node keeps under truncation. */
const TEXT_TRUNCATE_CHARS = 150;

/** What degradation, if any, was applied. */
export type DegradationLevel = 'none' | 'truncated' | 'interactive-only';

/** Result of budget enforcement. */
export interface BudgetResult {
  children: CSTNode[];
  tokenEstimate: number;
  degradation: DegradationLevel;
}

/** Estimate the token cost of a node list. */
function costOf(children: CSTNode[]): number {
  let total = 0;
  for (const node of children) total += estimateTokens(serializeCST(node));
  return total;
}

/** Truncate long text nodes recursively. */
function truncateText(node: CSTNode): CSTNode {
  if (isTextNode(node)) {
    if (node.content.length <= TEXT_TRUNCATE_CHARS) return node;
    return {
      type: 'text',
      content: `${node.content.slice(0, TEXT_TRUNCATE_CHARS)}… (truncated)`,
    };
  }
  if (hasChildren(node)) {
    return { ...node, children: node.children.map(truncateText) };
  }
  return node;
}

/** Keep only interactive nodes and the containers leading to them. */
function pruneToInteractive(node: CSTNode): CSTNode | null {
  if (node.type === 'interactive') return node;
  if (node.type === 'text') return null;
  if (hasChildren(node)) {
    const kept = node.children
      .map(pruneToInteractive)
      .filter((n): n is CSTNode => n !== null);
    if (kept.length === 0) return null;
    return { ...node, children: kept };
  }
  return node;
}

/**
 * Enforce the token budget on a captured node list via the degradation
 * ladder. Folding is assumed already applied (fold.ts).
 */
export function enforceBudget(
  children: CSTNode[],
  tokenBudget: number,
): BudgetResult {
  let cost = costOf(children);
  if (cost <= tokenBudget) {
    return { children, tokenEstimate: cost, degradation: 'none' };
  }

  // Pass 1 — truncate long text.
  const truncated = children.map(truncateText);
  cost = costOf(truncated);
  if (cost <= tokenBudget) {
    return { children: truncated, tokenEstimate: cost, degradation: 'truncated' };
  }

  // Pass 2 — interactive-only skeleton.
  const skeleton = truncated
    .map(pruneToInteractive)
    .filter((n): n is CSTNode => n !== null);
  cost = costOf(skeleton);
  return {
    children: skeleton,
    tokenEstimate: cost,
    degradation: 'interactive-only',
  };
}
