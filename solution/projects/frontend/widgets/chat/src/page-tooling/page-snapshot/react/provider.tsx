'use client';

import {
  type ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

import { useLocationProperty } from '@djangocfg/ui-core/hooks';

import {
  installChatBridge,
  setBridgeResolver,
} from '../../browser-bridge';

import type { CaptureEngineOptions, CaptureResult } from '../engine';
import { PageSnapshotEngine } from '../engine';
import {
  PageSnapshotContext,
  type PageSnapshotContextValue,
} from './use-page-snapshot';

/** Props for `PageSnapshotProvider`. */
export interface PageSnapshotProviderProps {
  /** Engine configuration. */
  config?: CaptureEngineOptions;
  /**
   * Opt-in value used when nothing is stored yet. Default false — the
   * user must explicitly enable sharing page context. Once the user
   * toggles it, the choice is persisted and this is ignored.
   */
  defaultLinked?: boolean;
  /**
   * Controlled opt-in. Supply BOTH `linked` and `onLinkedChange` to own the
   * value — typically by wiring chat's `useChatSettings().pageContext.linked`,
   * which is what the chat package does.
   *
   * Omit both and the provider falls back to its own `useState` seeded from
   * `defaultLinked`, so page-snapshot stays usable standalone.
   *
   * This inversion is deliberate: page-snapshot used to import
   * `useChatSettings` directly, which made a low-level capability depend on
   * the chat feature and formed the one cycle in the package graph. The host
   * that owns both now passes the value down.
   */
  linked?: boolean;
  /** Setter paired with `linked`. See `linked` for the controlled contract. */
  onLinkedChange?: (linked: boolean) => void;
  children: ReactNode;
}

/**
 * Provides the page-snapshot capability to the chat.
 *
 * - Constructs the engine lazily, browser-only (hydration-safe).
 * - Holds the opt-in state.
 * - `getChatMetadata` is the contributor handed to
 *   `ChatProvider.getDynamicMetadata`: it captures a fresh snapshot at
 *   send time (capture-on-submit) and returns `{ pageContext }`.
 * - Auto-captures on route change; tracks staleness via content hash.
 */
export function PageSnapshotProvider({
  config,
  defaultLinked = false,
  linked,
  onLinkedChange,
  children,
}: PageSnapshotProviderProps) {
  // The opt-in choice persists across sessions — the user enables screen
  // sharing once and it is remembered. Persistence belongs to whoever owns
  // the setting: the chat stores it in its centralized settings object
  // (`ChatSettings.pageContext.linked`) and passes it in. Uncontrolled use
  // keeps the value for the session only — a capability must not reach back
  // into a feature to find its own storage.
  const isControlled = linked !== undefined && onLinkedChange !== undefined;
  const [uncontrolledLinked, setUncontrolledLinked] = useState(defaultLinked);
  const isLinked = isControlled ? linked : uncontrolledLinked;
  const setIsLinked = isControlled ? onLinkedChange : setUncontrolledLinked;
  const [isStale, setIsStale] = useState(false);
  const [lastSnapshot, setLastSnapshot] = useState<CaptureResult | null>(null);

  // The snapshot that actually rode the most recent chat message.
  //
  // CST ref ids (`@eN`) are positional — assigned by DOM-order traversal
  // at capture time — so they are NOT stable across captures: `@e22` of
  // one snapshot need not be `@e22` of another. A `point` directive the
  // assistant returns cites refs from the snapshot it was given. To
  // resolve that directive correctly the overlay must use the registry
  // of *that* snapshot, not a newer one.
  //
  // `lastSnapshot` tracks the live page and is overwritten by every
  // route-change auto-capture, so it cannot be trusted for directive
  // resolution. This state holds the sent snapshot and is only ever
  // replaced on the next send — it survives route changes that happen
  // while a reply (and its directives) is still streaming in.
  const [sentSnapshot, setSentSnapshot] = useState<CaptureResult | null>(null);

  // Engine is browser-only. Construct it once, lazily, after mount —
  // a ref (not state) since it never needs to trigger a re-render.
  const engineRef = useRef<PageSnapshotEngine | null>(null);
  const getEngine = useCallback((): PageSnapshotEngine | null => {
    if (typeof window === 'undefined') return null;
    if (!engineRef.current) {
      engineRef.current = new PageSnapshotEngine(config);
    }
    return engineRef.current;
  }, [config]);

  // The hash the assistant last saw. Staleness is measured against THIS, not
  // against the newest capture: "the page changed" only matters relative to
  // what was sent, and `lastSnapshot` moves on every route change.
  const sentHashRef = useRef<string | null>(null);

  /**
   * Run a capture; on success update lastSnapshot + hash + staleness.
   *
   * Capture is synchronous (a DOM walk, single-digit ms) so there is no
   * `isProcessing` flag to toggle around it — that would only add two
   * needless re-renders.
   */
  const runCapture = useCallback(
    (track: boolean): CaptureResult | null => {
      const engine = getEngine();
      if (!engine) return null;
      try {
        const result = engine.capture();
        if (track) {
          setLastSnapshot(result);
          // Stale iff the page now differs from what the assistant was given.
          // Nothing sent yet ⇒ never stale: there is no claim to be stale
          // against, and a chip saying "changed" before the first turn would
          // be reporting on a snapshot nobody has seen.
          setIsStale(
            sentHashRef.current !== null &&
              result.payload.metadata.contentHash !== sentHashRef.current,
          );
        }
        return result;
      } catch {
        // Capture must never break the chat — fail soft.
        return null;
      }
    },
    [getEngine],
  );

  const capture = useCallback((): CaptureResult | null => {
    if (!isLinked) return null;
    return runCapture(true);
  }, [isLinked, runCapture]);

  const generatePreview = useCallback(
    (): CaptureResult | null => runCapture(false),
    [runCapture],
  );

  const refresh = useCallback(() => {
    runCapture(true);
  }, [runCapture]);

  /**
   * The chat metadata contributor. Captures fresh at call time — the
   * chat invokes this synchronously at send (capture-on-submit).
   */
  const getChatMetadata = useCallback((): Record<string, unknown> | undefined => {
    if (!isLinked) return undefined;
    const result = capture();
    if (!result) return undefined;
    // This is the snapshot the assistant will see — pin it so any
    // `point` directive in the reply resolves against the exact ref
    // registry that produced the refs the assistant cited.
    setSentSnapshot(result);
    sentHashRef.current = result.payload.metadata.contentHash;
    setIsStale(false);
    return { pageContext: result.payload };
  }, [isLinked, capture]);

  // Reactive pathname from ui-core's router abstraction. Framework-
  // agnostic (History API under the hood) — no next/navigation
  // dependency, works in Next / Vite / CRA / Electron alike.
  const pathname = useLocationProperty(
    () => window.location.pathname,
    () => '/',
  );

  // Route change → auto-capture a fresh snapshot (capture, not send).
  // Also covers the initial opt-in: when `isLinked` flips true this
  // effect runs and populates `lastSnapshot`.
  useEffect(() => {
    if (!isLinked) return;
    runCapture(true);
    // `pathname` in deps: a new route re-captures automatically.
  }, [isLinked, pathname, runCapture]);

  // Install the dev-only `window.__chatBridge` once — manual testing of
  // highlight / focus commands without an AI round-trip.
  useEffect(() => {
    installChatBridge();
  }, []);

  // Keep the bridge's ref resolver pointed at the latest snapshot, so
  // console-driven `window.__chatBridge.highlight()` commands resolve
  // refs against the current page. This is intentionally the *latest*
  // snapshot, not `sentSnapshot`: manual testing highlights what is on
  // screen now. AI-directive resolution is a separate path — it uses
  // `sentSnapshot` (see `DirectiveOverlay`) so it stays pinned to the
  // registry the assistant actually saw.
  useEffect(() => {
    setBridgeResolver(lastSnapshot?.refs ?? null);
    return () => setBridgeResolver(null);
  }, [lastSnapshot]);

  const value = useMemo<PageSnapshotContextValue>(
    () => ({
      isLinked,
      setIsLinked,
      capture,
      generatePreview,
      getChatMetadata,
      lastSnapshot,
      sentSnapshot,
      isStale,
      refresh,
    }),
    [
      isLinked,
      setIsLinked,
      capture,
      generatePreview,
      getChatMetadata,
      lastSnapshot,
      sentSnapshot,
      isStale,
      refresh,
    ],
  );

  return (
    <PageSnapshotContext.Provider value={value}>
      {children}
    </PageSnapshotContext.Provider>
  );
}
