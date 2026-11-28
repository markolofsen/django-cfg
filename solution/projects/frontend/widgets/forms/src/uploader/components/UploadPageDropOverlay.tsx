'use client';

import { useCallback, useEffect, useRef, useState, useMemo } from 'react';
import { useUploady } from '@rpldy/uploady';
import { Upload } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';
import { useT } from '@djangocfg/i18n';
import { getAssetTypeFromMime, logger } from '../utils';
import type { AssetType } from '../types';

export interface UploadPageDropOverlayProps {
  /** Allowed asset types */
  accept?: AssetType[];
  /** Max file size in MB */
  maxSizeMB?: number;
  /** Custom overlay content */
  children?: React.ReactNode;
  /** Custom class for overlay */
  className?: string;
  /** Callback when files are dropped */
  onFilesDropped?: (files: File[]) => void;
}

/** Returns true if a file's MIME type is allowed by the accepted asset types. */
function isAcceptedType(file: File, accept: AssetType[]): boolean {
  if (file.type) {
    if (file.type.startsWith('image/')) return accept.includes('image');
    if (file.type.startsWith('audio/')) return accept.includes('audio');
    if (file.type.startsWith('video/')) return accept.includes('video');
  }
  return accept.includes(file.type ? getAssetTypeFromMime(file.type) : 'document');
}

export function UploadPageDropOverlay({
  accept = ['image', 'audio', 'video', 'document'],
  maxSizeMB = 100,
  children,
  className,
  onFilesDropped,
}: UploadPageDropOverlayProps) {
  const t = useT();
  const { upload } = useUploady();
  const [isDragging, setIsDragging] = useState(false);
  const dragCounter = useRef(0);

  // Prepare data
  const maxBytes = maxSizeMB * 1024 * 1024;

  // Prepare labels
  const labels = useMemo(() => ({
    dropHere: t('tools.upload.dropHere'),
    uploading: t('tools.upload.uploading').replace('...', ''),
  }), [t]);

  // Prepare styles
  const overlayClassName = useMemo(() => cn(
    'fixed inset-0 z-50',
    'bg-background/80 backdrop-blur-sm',
    'flex items-center justify-center',
    'pointer-events-none',
    className
  ), [className]);

  // Handlers
  const handleFiles = useCallback((files: FileList | File[]) => {
    const fileArray = Array.from(files);

    const validFiles = fileArray.filter(file => {
      if (file.size > maxBytes) {
        logger.warn(`File "${file.name}" exceeds max size of ${maxSizeMB}MB`);
        return false;
      }
      if (!isAcceptedType(file, accept)) {
        logger.warn(`File "${file.name}" (${file.type || 'unknown'}) is not an accepted type`);
        return false;
      }
      return true;
    });

    if (validFiles.length > 0) {
      logger.info(`Page drop: ${validFiles.length} file(s)`);
      onFilesDropped?.(validFiles);
      upload(validFiles);
    }
  }, [upload, maxBytes, maxSizeMB, accept, onFilesDropped]);

  const handleDragEnter = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current++;

    if (e.dataTransfer?.items?.length) {
      setIsDragging(true);
    }
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;

    if (dragCounter.current === 0) {
      setIsDragging(false);
    }
  }, []);

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current = 0;
    setIsDragging(false);

    if (e.dataTransfer?.files?.length) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  // Setup event listeners
  useEffect(() => {
    document.addEventListener('dragenter', handleDragEnter);
    document.addEventListener('dragleave', handleDragLeave);
    document.addEventListener('dragover', handleDragOver);
    document.addEventListener('drop', handleDrop);

    return () => {
      document.removeEventListener('dragenter', handleDragEnter);
      document.removeEventListener('dragleave', handleDragLeave);
      document.removeEventListener('dragover', handleDragOver);
      document.removeEventListener('drop', handleDrop);
    };
  }, [handleDragEnter, handleDragLeave, handleDragOver, handleDrop]);

  // Early return when not dragging
  if (!isDragging) {
    return null;
  }

  // Prepare default content
  const defaultContent = (
    <div className="flex flex-col items-center gap-4 p-8 rounded-xl border-2 border-dashed border-primary bg-background/90">
      <Upload className="h-16 w-16 text-primary" aria-hidden="true" />
      <div className="text-center">
        <p className="text-lg font-medium">{labels.dropHere}</p>
        <p className="text-sm text-muted-foreground">{labels.uploading}</p>
      </div>
    </div>
  );

  return (
    <div className={overlayClassName} role="status" aria-live="polite">
      {children || defaultContent}
    </div>
  );
}
