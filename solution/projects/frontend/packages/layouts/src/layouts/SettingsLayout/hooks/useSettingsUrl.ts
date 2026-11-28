'use client';

/**
 * useSettingsUrl — two-way bind the SettingsDialog store to the URL hash.
 *
 * Shape: `#settings/<section>` (Claude.ai style). The leading key is
 * configurable (`urlKey`). Examples:
 *   #settings            → open, first/last-active section
 *   #settings/usage      → open, "usage" section active
 *   #settings/mcp?request=… → open on "mcp" with a one-shot intent (see `useSettingsIntent`); the query is stripped
 *   (no/other hash)      → closed
 *
 * Direction of truth:
 *   URL  → store : on mount and on every hashchange/popstate. This is what makes
 *                  deep-links, refresh, and the back button "just work" — the
 *                  browser owns history, we mirror it into state.
 *   store → URL : when the user opens/closes/switches section via the UI, we
 *                  push or replace the hash so it stays shareable.
 *
 * The URL fragment is read/written via ui-core's `useHashState`, which writes
 * straight to the History API (bypassing the router adapter) so the hash is set
 * absolutely — this is what avoids the `#settings#settings/…` doubling under
 * Next.js App Router + next-intl. It's framework-agnostic (Next / Wails / Vite).
 */

import { useEffect, useRef } from 'react';

import { useHashState } from '@djangocfg/ui-core/hooks';

import { buildSettingsHash as buildHash, parseSettingsHash as parseHash, sectionToOpen } from '../intent/parseSettingsHash';
import { useSettingsDialogStore } from '../store';

export interface UseSettingsUrlOptions {
  /** Hash namespace before the section id. Default: "settings". */
  urlKey?: string;
  /** Disable the binding entirely (imperative-only mode). Default: false. */
  enabled?: boolean;
  /**
   * Validate / normalize a section id read from the URL. Return null to reject
   * an unknown id (dialog still opens, on the fallback section; the id stays in
   * the address so a section registered a moment later can claim it). The shell
   * passes the set of known section ids here.
   */
  resolveSection?: (id: string | null) => string | null;
}

export function useSettingsUrl(options: UseSettingsUrlOptions = {}): void {
  const { urlKey = 'settings', enabled = true, resolveSection } = options;

  // Bare fragment (without '#'); '' when there is no hash.
  const [fragment, setFragment] = useHashState();

  const isOpen = useSettingsDialogStore((s) => s.isOpen);
  const activeSection = useSettingsDialogStore((s) => s.activeSection);
  const open = useSettingsDialogStore((s) => s.open);
  const close = useSettingsDialogStore((s) => s.close);
  const setIntent = useSettingsDialogStore((s) => s.setIntent);

  // Guard against the URL→store and store→URL effects fighting each other:
  // when we write the fragment ourselves we tag the value we wrote and skip the
  // next URL→store pass for that exact value.
  const selfWrittenFragment = useRef<string | null>(null);

  // ── URL → store ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!enabled) return;

    // Ignore the echo of a fragment we just wrote ourselves.
    if (selfWrittenFragment.current === fragment) {
      selfWrittenFragment.current = null;
      return;
    }

    const parsed = parseHash(fragment, urlKey);

    if (parsed.open) {
      // A section the host does not know *yet* stays in the address (see `sectionToOpen`).
      const resolved = sectionToOpen(parsed.section, resolveSection ? resolveSection(parsed.section) : parsed.section);
      // open() preserves the current section when called without one, so only
      // pass a section when the URL actually named a (valid) one.
      open(resolved ?? undefined);
      if (Object.keys(parsed.params).length > 0) {
        // A one-shot intent: hand it to the section, then strip the query so it is not shared, bookmarked or replayed.
        setIntent({ section: resolved, params: parsed.params });
        const stripped = buildHash(urlKey, resolved);
        selfWrittenFragment.current = stripped;
        setFragment(stripped, { replace: true });
      }
    } else if (isOpen) {
      // Hash no longer points at us (back button, manual edit) → close.
      close();
    }
    // We intentionally depend on `fragment` only; isOpen is read fresh via the
    // store getter semantics above. Re-running on isOpen would double-fire.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fragment, enabled, urlKey]);

  // ── store → URL ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!enabled) return;
    if (typeof window === 'undefined') return;

    const current = fragment;

    if (isOpen) {
      const next = buildHash(urlKey, activeSection);
      if (current !== next) {
        selfWrittenFragment.current = next;
        // Push when we're *opening* (no settings fragment yet) so the back
        // button closes the dialog; replace when only switching sections within
        // an already-open dialog, so section clicks don't stack history entries.
        const alreadyOurs = parseHash(current, urlKey).open;
        setFragment(next, { replace: alreadyOurs });
      }
    } else {
      // Only strip if the fragment is *ours*; never clobber an unrelated hash.
      if (parseHash(current, urlKey).open) {
        selfWrittenFragment.current = '';
        setFragment(null, { replace: true });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, activeSection, enabled, urlKey]);
}
