'use client';

import Uploady from '@rpldy/uploady';
import type { UploadyProps } from '@rpldy/uploady';
import type { ReactNode } from 'react';
import { UploadPageDropOverlay, type UploadPageDropOverlayProps } from '../components/UploadPageDropOverlay';

export interface UploadProviderProps extends Partial<UploadyProps> {
  children: ReactNode;
  /** Enable page-level drop zone */
  pageDropEnabled?: boolean;
  /** Props for page drop overlay */
  pageDropProps?: Omit<UploadPageDropOverlayProps, 'children'>;
  /** Custom overlay content for page drop */
  pageDropOverlay?: ReactNode;
}

const DEFAULT_OPTIONS: Partial<UploadyProps> = {
  autoUpload: true,
  concurrent: true,
  maxConcurrent: 3,
  inputFieldName: 'file',
};

export function UploadProvider({
  children,
  pageDropEnabled = false,
  pageDropProps,
  pageDropOverlay,
  ...options
}: UploadProviderProps) {
  return (
    <Uploady {...DEFAULT_OPTIONS} {...options}>
      {children}
      {pageDropEnabled && (
        <UploadPageDropOverlay {...pageDropProps}>
          {pageDropOverlay}
        </UploadPageDropOverlay>
      )}
    </Uploady>
  );
}
