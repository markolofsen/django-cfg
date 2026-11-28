'use client';

import { useRef, useCallback } from 'react';
import {
  useBatchFinishListener,
  useItemFinishListener,
  useItemErrorListener,
} from '@rpldy/uploady';
import { getAssetTypeFromMime } from '../utils';
import type { UploadedAsset } from '../types';

interface UseUploadEventsOptions {
  onFileComplete?: (asset: UploadedAsset, rawResponse: Record<string, unknown>) => void;
  onBatchComplete?: (assets: UploadedAsset[]) => void;
  onError?: (error: string, fileName: string, rawResponse: Record<string, unknown> | null) => void;
}

export function useUploadEvents(options?: UseUploadEventsOptions) {
  const { onFileComplete, onBatchComplete, onError } = options || {};
  const completedAssetsRef = useRef<UploadedAsset[]>([]);

  useItemFinishListener(useCallback((item) => {
    const response = item.uploadResponse?.data as Record<string, unknown> | undefined;
    const file = item.file as File;

    if (response) {
      const asset: UploadedAsset = {
        id: (response.id as string) || (response.uuid as string) || item.id,
        name: file.name,
        type: getAssetTypeFromMime(file.type),
        url: (response.url as string) || (response.file as string) || (response.file_url as string) || '',
        thumbnailUrl: (response.thumbnail_url as string) || (response.thumbnail as string) || (response.thumb_url as string),
        size: file.size,
        mimeType: file.type,
        duration: response.duration as number | undefined,
      };

      completedAssetsRef.current.push(asset);
      onFileComplete?.(asset, response);
    }
  }, [onFileComplete]));

  useItemErrorListener(useCallback((item) => {
    const file = item.file as File;
    const response = item.uploadResponse?.data as Record<string, unknown> | null;
    const message = (response?.message as string) || (response?.error as string) || (response?.detail as string) || 'Upload failed';
    onError?.(message, file.name, response);
  }, [onError]));

  useBatchFinishListener(useCallback(() => {
    if (completedAssetsRef.current.length > 0) {
      onBatchComplete?.(completedAssetsRef.current);
      completedAssetsRef.current = [];
    }
  }, [onBatchComplete]));
}
