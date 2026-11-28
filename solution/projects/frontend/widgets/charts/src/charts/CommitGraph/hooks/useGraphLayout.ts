// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { useMemo } from 'react';
import type { Commit, Edge, GraphRow } from '../types';
import { pickLaneColor } from './useLaneColors';

/**
 * Topological layout pass for the commit graph.
 *
 * Walks the commit list in order (newest first) and tracks active rails —
 * each slot holds the hash of the parent the rail is "waiting for". The
 * algorithm produces:
 *
 *  - The rail a commit's dot occupies.
 *  - The rails state after the row (for the next iteration).
 *  - Edges to draw on this row (pass-throughs, merge curves, fork curves).
 *
 * Rail colors are looked up at layout time so the rendered SVG can use raw
 * hex `stroke=` values — Canvas2D/SVG won't parse Tailwind classes.
 */
function computeLayout(commits: Commit[], laneColors: string[]): GraphRow[] {
  const rows: GraphRow[] = [];
  const rails: (string | null)[] = [];
  const color = (rail: number) => pickLaneColor(laneColors, rail);

  for (const commit of commits) {
    const hash = commit.hash;

    // Find which rail this commit occupies (if any rail is waiting for it).
    let commitRail = rails.indexOf(hash);

    if (commitRail === -1) {
      // New branch — find first empty slot or append.
      const emptySlot = rails.indexOf(null);
      if (emptySlot !== -1) {
        commitRail = emptySlot;
        rails[commitRail] = hash;
      } else {
        commitRail = rails.length;
        rails.push(hash);
      }
    }

    const commitColor = color(commitRail);
    const edges: Edge[] = [];

    // Pass-through rails (everything not on the commit rail).
    for (let r = 0; r < rails.length; r++) {
      if (r !== commitRail && rails[r] !== null) {
        edges.push({ fromRail: r, toRail: r, color: color(r), type: 'straight' });
      }
    }

    // Clear this rail — the commit has been rendered.
    rails[commitRail] = null;

    // First parent continues on the commit's rail unless already expected
    // elsewhere (merge of two existing branches).
    const parents = commit.parents;
    const firstParent = parents[0];
    if (firstParent !== undefined) {
      const existingRail = rails.indexOf(firstParent);
      if (existingRail !== -1) {
        edges.push({
          fromRail: commitRail,
          toRail: existingRail,
          color: commitColor,
          type: 'merge-in',
        });
      } else {
        rails[commitRail] = firstParent;
        edges.push({
          fromRail: commitRail,
          toRail: commitRail,
          color: commitColor,
          type: 'straight',
        });
      }
    }

    // Second+ parents (merge sources / forks).
    for (let p = 1; p < parents.length; p++) {
      const parentHash = parents[p];
      if (parentHash === undefined) continue;
      const existingRail = rails.indexOf(parentHash);
      if (existingRail !== -1) {
        edges.push({
          fromRail: existingRail,
          toRail: commitRail,
          color: color(existingRail),
          type: 'merge-in',
        });
      } else {
        const emptySlot = rails.indexOf(null);
        const newRail = emptySlot !== -1 ? emptySlot : rails.length;
        if (newRail >= rails.length) rails.push(null);
        rails[newRail] = parentHash;
        edges.push({
          fromRail: commitRail,
          toRail: newRail,
          color: color(newRail),
          type: 'fork-out',
        });
      }
    }

    // Trim trailing nulls so `maxRails` stays accurate.
    while (rails.length > 0 && rails[rails.length - 1] === null) {
      rails.pop();
    }

    rows.push({
      commit,
      rail: commitRail,
      rails: [...rails],
      edges,
    });
  }

  return rows;
}

/**
 * Auto-infer a linear topology when no commit declares parents — the
 * jalcoui examples ship a flat list and rely on the component to chain
 * them.
 */
function ensureTopology(commits: Commit[]): Commit[] {
  const hasTopology = commits.some((c) => c.parents && c.parents.length > 0);
  if (hasTopology) return commits;
  return commits.map((c, i) => {
    const next = commits[i + 1];
    return { ...c, parents: next ? [next.hash] : [] };
  });
}

export interface GraphLayout {
  rows: GraphRow[];
  maxRails: number;
}

/**
 * React-friendly wrapper around {@link computeLayout}. Memoizes on
 * `commits` + `laneColors` identity so theme switches re-color but do not
 * reshuffle topology.
 */
export function useGraphLayout(
  commits: Commit[],
  laneColors: string[],
): GraphLayout {
  return useMemo(() => {
    const resolved = ensureTopology(commits);
    if (resolved.length === 0) {
      return { rows: [], maxRails: 0 };
    }
    const rows = computeLayout(resolved, laneColors);
    const maxRails = Math.max(
      ...rows.map((r) =>
        Math.max(
          r.rail + 1,
          r.rails.length,
          ...r.edges.map((e) => Math.max(e.fromRail, e.toRail) + 1),
        ),
      ),
    );
    return { rows, maxRails };
  }, [commits, laneColors]);
}
