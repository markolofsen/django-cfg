'use client';

/**
 * Lazy-loaded OpenapiViewer Component
 *
 * Heavy OpenAPI viewer (~400KB) is loaded only when component is rendered.
 * Use this for automatic code-splitting with Suspense fallback.
 *
 * For direct imports without lazy loading, use:
 *   import OpenapiViewer from '@djangocfg/widget-chat-dev/openapi'
 */

import * as React from 'react';
import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import { PlaygroundProvider } from './context/PlaygroundContext';
import type { ApiKey, PlaygroundConfig, SchemaSource } from './types';

export interface PlaygroundProps {
  config: PlaygroundConfig;
}

export type { ApiKey, PlaygroundConfig, SchemaSource };

function OpenapiLoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-[400px] bg-muted/30 rounded-lg">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent" />
        <p className="mt-3 text-sm text-muted-foreground">Loading API Playground...</p>
      </div>
    </div>
  );
}

// `DocsLayout` takes no props; name the type parameter so the loader's promise
// is not widened to `ComponentType<never>`.
const LazyDocsLayout = createLazyComponent<Record<string, never>>(
  () => import('./components/DocsLayout').then((mod) => ({ default: mod.DocsLayout })),
  {
    displayName: 'LazyDocsLayout',
    fallback: <OpenapiLoadingFallback />,
  }
);

export const LazyOpenapiViewer: React.FC<PlaygroundProps> = ({ config }) => {
  return (
    <PlaygroundProvider config={config}>
      <LazyDocsLayout />
    </PlaygroundProvider>
  );
};

LazyOpenapiViewer.displayName = 'LazyOpenapiViewer';
