'use client';

import * as React from 'react';
import type { ErrorInfo } from 'react';

import { TooltipProvider } from '../components/overlay/tooltip';
import { Toaster } from '../components/feedback/sonner';
import { Boundary, type BoundaryProps } from '../components/boundary';
import { syncDisplayModeAttribute } from '../hooks/media/displayMode';
import { syncViewport } from '../hooks/media/viewportSync';
import { syncViewportDebug } from '../hooks/media/viewportDebug';
import { installChunkReloadListeners } from '../lib/chunk-reload';
import { DialogProvider } from '../lib/dialog-service/DialogProvider';

export interface UiProvidersProps {
  children: React.ReactNode;
  /**
   * Show the viewport diagnostic dot even when nobody turned the HUD on (a host with no Settings dialog: a call page).
   * Tapping the dot opens the HUD; a state stored in `localStorage` still wins. @default false
   */
  debug?: boolean;
  /** Tooltip open delay in ms. @default 100 (snappy for desktop apps) */
  tooltipDelay?: number;
  /** Disable the Sonner toaster (e.g. when the host renders its own). */
  noToaster?: boolean;
  /** Disable the imperative `window.dialog` service + its renderer. */
  noDialogService?: boolean;
  /**
   * Top-level crash protection. By default UiProviders wraps the whole tree in
   * a fullscreen `<Boundary>` so any uncaught React error shows a recoverable
   * fallback instead of a white screen. Pass `onError` to forward the crash to
   * your logger / monitor (the host owns logging; the boundary just calls it).
   * Set `errorBoundary={false}` if the host installs its own top-level boundary.
   */
  onError?: (error: Error, info: ErrorInfo) => void;
  /** Disable the built-in top-level error boundary. @default false (boundary on) */
  errorBoundary?: false;
  /**
   * Custom fallback for the built-in boundary. Receives `{ error, errorInfo,
   * reset }`. Use it to render an app-specific (e.g. i18n'd) crash screen
   * instead of the default fullscreen one — lets hosts keep a single boundary
   * (this one) rather than wrapping their own on top.
   */
  errorFallback?: BoundaryProps['fallback'];
  /**
   * SSR-safe mount strategy. Default `true` — skips providers on the
   * initial server render and remounts after `useEffect` so Radix
   * `<TooltipProvider>` (which calls `useId()` + opens internal state
   * on mount) doesn't trigger hydration mismatches under Next.js.
   *
   * Set `ssr={false}` on CSR-only hosts (Wails, Vite SPA, Storybook
   * iframe) to skip the deferred mount — providers render on the
   * very first paint and library components see their context
   * immediately.
   */
  ssr?: boolean;
}

/**
 * One root composition for every overlay/imperative-service the
 * djangocfg UI library needs:
 *
 *  - `<TooltipProvider>` — single context root for every `<Tooltip>`
 *    in the tree (Radix). Without one, library components log
 *    "Tooltip must be used within TooltipProvider".
 *  - `<DialogProvider>`  — installs the `window.dialog.*` imperative
 *    API and renders the active dialog into a portal.
 *  - `<Toaster>`         — Sonner toast portal. Library callsites use
 *    `toast(...)` from the same package; no portal = silent no-op.
 *
 * Apple-style: app/host mounts ONE `<UiProviders>` at the very top of
 * the tree, and never again. Library components must NOT include their
 * own nested `TooltipProvider` — a second context root creates a fresh
 * provider scope with different delays, and (worse) under Vite dev a
 * dup-module load yields two `createContext()` instances, breaking the
 * provider/consumer link.
 *
 * Usage:
 *   import { UiProviders } from '@djangocfg/ui-core/lib/providers';
 *
 *   <UiProviders>
 *     <YourApp />
 *   </UiProviders>
 */
export function UiProviders({
  children,
  debug = false,
  tooltipDelay = 100,
  noToaster,
  noDialogService,
  onError,
  errorBoundary,
  errorFallback,
}: UiProvidersProps) {
  // Stale tab after a deploy: reload once on chunk-load failures outside React.
  React.useEffect(() => installChunkReloadListeners(), []);
  // `<html data-display-mode="browser|standalone|...">` for CSS (see styles/css/base.css tokens).
  React.useEffect(() => syncDisplayModeAttribute(), []);
  // Installed app viewport: `--app-height` and a shell at scroll 0 (see hooks/media/viewportSync).
  React.useEffect(() => syncViewport(), []);
  // The Settings > Debug switch prints scroll, body/html style and viewport numbers on screen; off otherwise.
  React.useEffect(() => syncViewportDebug({ debug }), [debug]);
  // No SSR-skip on purpose: any nested library component that renders
  // `<Tooltip>` on its first paint expects to find `<TooltipProvider>`
  // already in the tree. Skipping the provider during SSR caused
  // "Tooltip must be used within TooltipProvider" before hydration.
  // Radix's own provider tolerates the SSR pass — no hydration
  // mismatches observed; the safe wrapper was over-engineering.
  const dialogTree = noDialogService ? children : <DialogProvider>{children}</DialogProvider>;
  // Top-level crash protection by default. The Boundary catches uncaught React
  // errors and shows a recoverable fullscreen fallback; `onError` forwards the
  // crash to the host's logger/monitor. Opt out with `errorBoundary={false}`.
  const tree =
    errorBoundary === false ? (
      dialogTree
    ) : (
      <Boundary
        variant="fullscreen"
        name="ui-providers"
        onError={onError}
        fallback={errorFallback}
      >
        {dialogTree}
      </Boundary>
    );
  return (
    <TooltipProvider delayDuration={tooltipDelay}>
      {tree}
      {!noToaster && <Toaster />}
    </TooltipProvider>
  );
}
