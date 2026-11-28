/**
 * Sibling folding — collapse repetitive structure.
 *
 * Always-on, applied to every node list. Structurally-identical sibling
 * chains (table rows, list items, grid cells) collapse to "first N +
 * a collapsed marker". This is what makes a 100-row data table fit the
 * token budget — without it a 100-row table snapshot is ~10x over.
 *
 */

import type { CSTNode } from '../cst/types';
import { hasChildren } from '../cst/types';

/** How many leading instances of a repeated chain to keep. */
const KEEP_LEADING = 3;
/** A chain shorter than this is never folded. */
const MIN_CHAIN = 5;

/** Result of a folding pass. */
export interface FoldResult {
  /** The folded tree. */
  children: CSTNode[];
  /** How many sibling chains were folded. */
  foldedCount: number;
}

/**
 * A shallow structural hash of a node — its shape, not its content.
 * Two nodes with the same hash are "the same kind of thing" (e.g. two
 * table rows), regardless of the text they hold.
 */
function structuralHash(node: CSTNode): string {
  switch (node.type) {
    case 'text':
      return 't';
    case 'interactive':
      return `i:${node.role}`;
    case 'container':
      return `c:${node.role}:[${node.children
        .map(structuralHash)
        .join(',')}]`;
    case 'root':
      return 'root';
  }
}

/** Counter threaded through a recursive fold so totals aggregate. */
interface FoldCtx {
  folded: number;
}

/** Fold one list of sibling nodes. */
function foldList(nodes: CSTNode[], ctx: FoldCtx): CSTNode[] {
  // Recurse first so nested lists are folded before the outer pass.
  const deep = nodes.map((n) => foldNode(n, ctx));

  const out: CSTNode[] = [];
  let i = 0;
  while (i < deep.length) {
    const head = deep[i];
    if (head === undefined) break;
    const hash = structuralHash(head);
    // Extend the run of identically-shaped siblings.
    let j = i + 1;
    for (; j < deep.length; j++) {
      const sibling = deep[j];
      if (sibling === undefined || structuralHash(sibling) !== hash) break;
    }
    const runLength = j - i;

    if (runLength >= MIN_CHAIN) {
      // Keep the leading N, collapse the rest into one marker.
      for (let k = i; k < i + KEEP_LEADING; k++) {
        const kept = deep[k];
        if (kept !== undefined) out.push(kept);
      }
      const collapsed = runLength - KEEP_LEADING;
      out.push({
        type: 'text',
        content: `[… ${collapsed} more similar items collapsed]`,
      });
      ctx.folded++;
    } else {
      for (let k = i; k < j; k++) {
        const kept = deep[k];
        if (kept !== undefined) out.push(kept);
      }
    }
    i = j;
  }
  return out;
}

/** Recursively fold a single node's children. */
function foldNode(node: CSTNode, ctx: FoldCtx): CSTNode {
  if (!hasChildren(node)) return node;
  return { ...node, children: foldList(node.children, ctx) };
}

/**
 * Fold repetitive sibling chains within a node list.
 */
export function foldSiblings(children: CSTNode[]): FoldResult {
  const ctx: FoldCtx = { folded: 0 };
  const folded = foldList(children, ctx);
  return { children: folded, foldedCount: ctx.folded };
}
