// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type * as React from 'react';

/**
 * Author metadata rendered next to each commit row and inside the detail
 * popover. Avatar URLs are optional — when omitted, the initials of
 * {@link CommitAuthor.name} are shown instead.
 */
export interface CommitAuthor {
  name: string;
  avatarUrl?: string;
}

/**
 * Single commit node fed into {@link CommitGraph}. Commits must be passed in
 * topological order (newest first). The `parents` array drives the rail
 * topology — empty for root commits, one entry for normal commits, two or
 * more for merges.
 */
export interface Commit {
  /** Commit hash (full or abbreviated). */
  hash: string;
  /** Commit message (first line). */
  message: string;
  /** Commit author. */
  author: CommitAuthor;
  /** ISO date string or Date object. */
  date: string | Date;
  /** Parent commit hashes. Empty for root commits. Two parents = merge commit. */
  parents: string[];
  /** Branch or ref labels (e.g. `"main"`, `"feat/auth"`). */
  refs?: string[];
  /** Tag label (e.g. `"v1.0.0"`). */
  tag?: string;
}

/**
 * Props for {@link CommitGraph}.
 */
export interface CommitGraphProps
  extends Omit<React.ComponentProps<'div'>, 'children'> {
  /** Commits in topological order (newest first). */
  commits: Commit[];
  /** Number of hash characters to display. @default 7 */
  truncateHash?: number;
  /** Pixel width per rail column. @default 24 */
  railWidth?: number;
}

/**
 * Type of edge a rail segment renders inside a row. The layout pass tags
 * every drawn segment with one of these — the SVG renderer only needs to
 * pick the geometry per type.
 */
export type EdgeType = 'straight' | 'merge-in' | 'fork-out';

/**
 * A single edge inside a {@link GraphRow}. Indices refer to rail slots
 * (left-to-right) and `color` is a hex string already resolved through the
 * theme palette — never a raw scale.
 */
export interface Edge {
  fromRail: number;
  toRail: number;
  color: string;
  type: EdgeType;
}

/**
 * Output of {@link computeLayout}. One row per commit, with the rail
 * topology snapshot needed to draw rails + edges.
 */
export interface GraphRow {
  commit: Commit;
  /** Rail index this commit's dot occupies. */
  rail: number;
  /** Rails state after this row (`null` = empty slot). */
  rails: (string | null)[];
  /** Edges to draw between the previous row and this row. */
  edges: Edge[];
}

/** Pixel height of a single commit row. */
export const ROW_HEIGHT = 40;
