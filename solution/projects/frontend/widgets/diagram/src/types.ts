/**
 * The renderer's props.
 *
 * In their own module because both the barrel and `lazy.tsx` need them, and
 * having `lazy` import them from the barrel while the barrel re-exports `lazy`
 * is a cycle — one that resolves at build time and bites at runtime.
 */

export interface MermaidProps {
  chart: string;
  className?: string;
  isCompact?: boolean;
  /** Enable click-to-fullscreen functionality (default: true) */
  fullscreen?: boolean;
  /**
   * Enable the FloatingToolbar's "click to scroll" lock overlay.
   * Defaults to `false` — Mermaid diagrams don't scroll internally,
   * so the lock overlay just steals page wheel events. See the
   * Mermaid.client implementation for the full rationale.
   */
  scrollIsolation?: boolean;
  /**
   * Debounce window (ms) before (re)rendering after `chart` changes.
   * Lower feels snappier for static charts; higher reduces churn while
   * a diagram is streamed in. Default 300.
   */
  debounceMs?: number;
}
