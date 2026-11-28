'use client';

import { useCallback, useEffect, useRef } from 'react';

/** Hash format: ``#<schemaId>/<anchor>``.
 *  - ``#catalog/ep-get-users`` — specific endpoint in ``catalog`` schema
 *  - ``#catalog`` — open ``catalog`` schema at its top
 *  - empty — no initial target, leave viewer at its default
 *
 *  We intentionally keep this opinionated and stringly-typed: the host app
 *  already controls which schemas exist, so there is no room for ambiguity
 *  beyond the two segments. */
export interface ParsedHash {
  schemaId: string | null;
  anchor: string | null;
}

export function parseDocsHash(hash: string): ParsedHash {
  const raw = hash.startsWith('#') ? hash.slice(1) : hash;
  if (!raw) return { schemaId: null, anchor: null };
  const [schemaId = null, ...rest] = raw.split('/');
  const anchor = rest.length > 0 ? rest.join('/') : null;
  return {
    schemaId: schemaId || null,
    anchor: anchor || null,
  };
}

export function buildDocsHash(schemaId: string | null, anchor: string | null): string {
  if (!schemaId && !anchor) return '';
  if (schemaId && anchor) return `#${schemaId}/${anchor}`;
  if (schemaId) return `#${schemaId}`;
  return anchor ? `#${anchor}` : '';
}

interface UseDocsUrlSyncProps {
  enabled: boolean;
  currentSchemaId: string | null;
  activeAnchor: string | null;
  /** Called on mount / ``popstate`` / ``hashchange`` with the hash state.
   *  The consumer is responsible for dispatching into its own handlers
   *  (switching schema, scrolling to endpoint) in the right order. */
  onHashTarget: (target: ParsedHash) => void;
}

/** Two-way sync between browser hash and docs viewer state.
 *
 *  - Writes use ``history.replaceState`` so scrollspy-driven updates don't
 *    pollute the back/forward stack. User-initiated navigation (click on
 *    sidebar row, schema switch) still lands in history because the click
 *    itself already did ``pushState`` — or will, via plain anchor hrefs.
 *  - Reads happen on mount (initial target) and on ``popstate`` /
 *    ``hashchange`` (Back/Forward / external anchor clicks).
 *  - When ``enabled`` is false, the hook is a no-op — the viewer stays
 *    hash-free so you can embed it inside a larger page. */
export function useDocsUrlSync({
  enabled,
  currentSchemaId,
  activeAnchor,
  onHashTarget,
}: UseDocsUrlSyncProps) {
  // Ignore the very first write — otherwise on mount we'd clobber the
  // incoming hash with the viewer's empty defaults before ``onHashTarget``
  // has a chance to apply it.
  const primedRef = useRef(false);
  const onHashTargetRef = useRef(onHashTarget);
  useEffect(() => {
    onHashTargetRef.current = onHashTarget;
  }, [onHashTarget]);

  // Read: mount + hashchange/popstate
  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;

    const apply = () => {
      onHashTargetRef.current(parseDocsHash(window.location.hash));
    };
    apply();
    primedRef.current = true;

    window.addEventListener('hashchange', apply);
    window.addEventListener('popstate', apply);
    return () => {
      window.removeEventListener('hashchange', apply);
      window.removeEventListener('popstate', apply);
    };
  }, [enabled]);

  // Write: whenever the viewer's state changes
  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;
    if (!primedRef.current) return;

    const next = buildDocsHash(currentSchemaId, activeAnchor);
    const current = window.location.hash;
    if (next === current) return;

    // replaceState keeps Back/Forward meaningful — a single scroll-through
    // the page shouldn't create 50 history entries.
    const url = next
      ? `${window.location.pathname}${window.location.search}${next}`
      : `${window.location.pathname}${window.location.search}`;
    window.history.replaceState(window.history.state, '', url);
  }, [enabled, currentSchemaId, activeAnchor]);

  const pushTarget = useCallback(
    (schemaId: string | null, anchor: string | null) => {
      if (!enabled || typeof window === 'undefined') return;
      const next = buildDocsHash(schemaId, anchor);
      const url = next
        ? `${window.location.pathname}${window.location.search}${next}`
        : `${window.location.pathname}${window.location.search}`;
      window.history.pushState(window.history.state, '', url);
    },
    [enabled],
  );

  return { pushTarget };
}
