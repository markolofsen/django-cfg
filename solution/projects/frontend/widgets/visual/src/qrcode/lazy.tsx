'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { QRCodeProps } from './types';

export const LazyQRCode = createLazyComponent<QRCodeProps>(
  () => import('./QRCode').then((mod) => ({ default: mod.QRCode })),
  {
    displayName: 'LazyQRCode',
    fallback: (
      <div
        data-slot="qr-code-skeleton"
        className="h-[200px] w-[200px] animate-pulse rounded-sm bg-muted"
      />
    ),
  }
);

export type { QRCodeProps } from './types';
