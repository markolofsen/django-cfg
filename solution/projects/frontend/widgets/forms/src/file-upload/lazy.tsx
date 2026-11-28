'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { FileUploadProps } from './types';

export const LazyFileUpload = createLazyComponent<FileUploadProps>(
  () => import('./FileUpload').then((mod) => ({ default: mod.FileUpload })),
  {
    displayName: 'LazyFileUpload',
    fallback: (
      <div className="flex flex-col gap-2">
        <div className="h-24 w-full animate-pulse rounded-lg bg-muted" />
        <div className="h-12 w-full animate-pulse rounded-lg bg-muted" />
      </div>
    ),
  }
);

export type { FileUploadProps } from './types';
