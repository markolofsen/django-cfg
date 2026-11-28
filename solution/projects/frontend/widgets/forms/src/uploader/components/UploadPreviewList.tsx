'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import {
  useBatchAddListener,
  useItemProgressListener,
  useItemFinishListener,
  useItemErrorListener,
  useItemAbortListener,
  useAbortItem,
  useUploady,
} from '@rpldy/uploady';
import { cn } from '@djangocfg/ui-core/lib';
import { UploadPreviewItem } from './UploadPreviewItem';
import {
  buildAssetFromResponse,
  extractErrorMessage,
} from '../utils';
import type { UploadItem, UploadPreviewListProps } from '../types';

export function UploadPreviewList({
  className,
  onRemove,
  onRetry,
  showThumbnails = true,
}: UploadPreviewListProps) {
  const [items, setItems] = useState<Map<string, UploadItem>>(new Map());
  const abortItem = useAbortItem();
  const { upload } = useUploady();

  // Live ref to items so unmount cleanup sees the latest object URLs
  // (a [] effect would only ever capture the initial empty Map).
  const itemsRef = useRef(items);
  itemsRef.current = items;

  // Batch added - create initial items
  useBatchAddListener((batch) => {
    setItems(prev => {
      const next = new Map(prev);
      batch.items.forEach(item => {
        const file = item.file as File;
        let previewUrl: string | undefined;

        // Create object URL for image/video preview
        if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
          previewUrl = URL.createObjectURL(file);
        }

        next.set(item.id, {
          id: item.id,
          file,
          status: 'pending',
          progress: 0,
          previewUrl,
        });
      });
      return next;
    });
  });

  // Progress update
  useItemProgressListener((item) => {
    setItems(prev => {
      const next = new Map(prev);
      const existing = next.get(item.id);
      if (existing) {
        next.set(item.id, {
          ...existing,
          status: 'uploading',
          progress: item.completed,
        });
      }
      return next;
    });
  });

  // Upload complete
  useItemFinishListener((item) => {
    setItems(prev => {
      const next = new Map(prev);
      const existing = next.get(item.id);
      if (existing) {
        const response = item.uploadResponse?.data as Record<string, unknown> | undefined;
        const asset = response
          ? buildAssetFromResponse(response, existing.file)
          : undefined;

        // The server now hosts the file — revoke the local object URL so it
        // can be garbage-collected, and keep only a server-hosted preview URL.
        if (existing.previewUrl) {
          URL.revokeObjectURL(existing.previewUrl);
        }

        next.set(item.id, {
          ...existing,
          status: 'complete',
          progress: 100,
          asset,
          previewUrl: asset?.thumbnailUrl || asset?.url || undefined,
        });
      }
      return next;
    });
  });

  // Error
  useItemErrorListener((item) => {
    setItems(prev => {
      const next = new Map(prev);
      const existing = next.get(item.id);
      if (existing) {
        const response = item.uploadResponse?.data as Record<string, unknown> | null;
        const status = item.uploadResponse?.status || 0;
        const error = extractErrorMessage(response, status);

        next.set(item.id, {
          ...existing,
          status: 'error',
          error,
        });
      }
      return next;
    });
  });

  // Aborted
  useItemAbortListener((item) => {
    setItems(prev => {
      const next = new Map(prev);
      const existing = next.get(item.id);
      if (existing) {
        next.set(item.id, {
          ...existing,
          status: 'aborted',
        });
      }
      return next;
    });
  });

  // Handle remove
  const handleRemove = useCallback((id: string) => {
    const item = items.get(id);
    if (item) {
      // Abort if uploading
      if (item.status === 'uploading') {
        abortItem(id);
      }
      // Revoke object URL
      if (item.previewUrl) {
        URL.revokeObjectURL(item.previewUrl);
      }
    }

    setItems(prev => {
      const next = new Map(prev);
      next.delete(id);
      return next;
    });

    onRemove?.(id);
  }, [items, abortItem, onRemove]);

  // Handle retry
  const handleRetry = useCallback((id: string) => {
    const item = items.get(id);
    if (item && (item.status === 'error' || item.status === 'aborted')) {
      // rpldy.upload() creates a NEW batch item with a fresh id, so the old
      // entry must be dropped (and its object URL revoked) to avoid a stale
      // ghost item and a leaked URL. useBatchAddListener adds the new one.
      if (item.previewUrl) {
        URL.revokeObjectURL(item.previewUrl);
      }
      setItems(prev => {
        const next = new Map(prev);
        next.delete(id);
        return next;
      });

      // Re-upload the file
      upload(item.file);
      onRetry?.(id);
    }
  }, [items, upload, onRetry]);

  // Cleanup object URLs on unmount (reads live ref, not a stale closure)
  useEffect(() => {
    return () => {
      itemsRef.current.forEach(item => {
        if (item.previewUrl) {
          URL.revokeObjectURL(item.previewUrl);
        }
      });
    };
  }, []);

  const itemsArray = Array.from(items.values());

  if (itemsArray.length === 0) {
    return null;
  }

  return (
    <div className={cn('space-y-2', className)}>
      {itemsArray.map(item => (
        <UploadPreviewItem
          key={item.id}
          item={item}
          onRemove={handleRemove}
          onRetry={handleRetry}
          showThumbnail={showThumbnails}
        />
      ))}
    </div>
  );
}
