'use client';

import React, { lazy, Suspense } from 'react';
import { PlaygroundProvider } from './context/PlaygroundContext';
import type { PlaygroundConfig } from './types';

const DocsLayout = lazy(() =>
  import('./components/DocsLayout').then((mod) => ({ default: mod.DocsLayout }))
);

const LoadingFallback = () => (
  <div className="flex items-center justify-center min-h-[400px]">
    <div className="text-muted-foreground">Loading API Playground...</div>
  </div>
);

export interface PlaygroundProps {
  config: PlaygroundConfig;
}

export const Playground: React.FC<PlaygroundProps> = ({ config }) => {
  return (
    <PlaygroundProvider config={config}>
      <Suspense fallback={<LoadingFallback />}>
        <DocsLayout />
      </Suspense>
    </PlaygroundProvider>
  );
};

export type { PlaygroundConfig, SchemaSource } from './types';

export default Playground;
