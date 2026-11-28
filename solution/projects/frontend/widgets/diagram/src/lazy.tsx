'use client';

/**
 * The renderer's single lazy boundary.
 *
 * `mermaid` unpacks to ~84 MB, so it must never be a static edge. The barrel
 * re-exports what is here rather than wrapping it a second time.
 */

import { createLazyComponent, CardLoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { MermaidProps } from './types';

// ============================================================================
// Types
// ============================================================================

export type { MermaidProps };

// ============================================================================
// Lazy Component
// ============================================================================

/**
 * LazyMermaid - Lazy-loaded Mermaid diagram renderer
 *
 * Automatically shows loading state while Mermaid loads (~800KB)
 */
export const LazyMermaid = createLazyComponent<MermaidProps>(
  () => import('./Mermaid.client'),
  {
    displayName: 'LazyMermaid',
    fallback: (
      <CardLoadingFallback
        title="Diagram"
        description="Loading..."
        minHeight={200}
      />
    ),
  }
);
