'use client';

/**
 * Lazy-loaded JsonForm Component
 *
 * Heavy JSON Schema Form (~300KB) is loaded only when component is rendered.
 * Use this for automatic code-splitting with Suspense fallback.
 *
 * For direct imports without lazy loading, use:
 * import { JsonSchemaForm } from '@djangocfg/widget-forms/json-form'
 */

import { createLazyComponent, CardLoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { JsonSchemaFormProps } from './types';

// ============================================================================
// Re-export types
// ============================================================================

export type { JsonSchemaFormProps };

// ============================================================================
// Lazy Component
// ============================================================================

/**
 * LazyJsonSchemaForm - Lazy-loaded JSON Schema form generator
 *
 * Automatically shows loading state while RJSF loads (~300KB)
 */
export const LazyJsonSchemaForm = createLazyComponent<JsonSchemaFormProps>(
  () => import('./JsonSchemaForm').then((mod) => ({ default: mod.JsonSchemaForm })),
  {
    displayName: 'LazyJsonSchemaForm',
    fallback: (
      <CardLoadingFallback
        title="Form"
        description="Loading form schema..."
        minHeight={200}
      />
    ),
  }
);
