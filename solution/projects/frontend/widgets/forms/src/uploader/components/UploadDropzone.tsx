'use client';

import { useCallback, useRef, useState, useMemo } from 'react';
import { useUploady } from '@rpldy/uploady';
import { Upload } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';
import { useT } from '@djangocfg/i18n';
import { buildAcceptString, getAssetTypeFromMime, logger } from '../utils';
import { useClipboardPaste } from '../hooks/useClipboardPaste';
import type { AssetType, UploadDropzoneProps } from '../types';

/** Returns true if a file's MIME type is allowed by the accepted asset types. */
function isAcceptedType(file: File, accept: AssetType[]): boolean {
  // image/audio/video are matched by prefix so unknown subtypes still pass.
  if (file.type) {
    if (file.type.startsWith('image/')) return accept.includes('image');
    if (file.type.startsWith('audio/')) return accept.includes('audio');
    if (file.type.startsWith('video/')) return accept.includes('video');
  }
  // No/other MIME type — fall back to asset detection (defaults to document).
  return accept.includes(file.type ? getAssetTypeFromMime(file.type) : 'document');
}

function useOptionalUploady(uploadFn?: (files: File[]) => void) {
  try {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { upload } = useUploady();
    return uploadFn ?? upload;
  } catch {
    // Not inside UploadProvider — use uploadFn if provided, otherwise noop
    return uploadFn ?? (() => {});
  }
}

export function UploadDropzone({
  accept = ['image', 'audio', 'video', 'document'],
  multiple = true,
  maxSizeMB = 100,
  compact = false,
  disabled = false,
  className,
  children,
  onFilesSelected,
  uploadFn,
  pasteEnabled = true,
  onPasteNoMatch,
}: UploadDropzoneProps) {
  const t = useT();
  const upload = useOptionalUploady(uploadFn);
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [rejectedCount, setRejectedCount] = useState(0);
  const dragCounter = useRef(0);

  // Prepare data
  const acceptString = useMemo(() => buildAcceptString(accept), [accept]);
  const maxBytes = maxSizeMB * 1024 * 1024;

  // Prepare labels
  const labels = useMemo(() => ({
    dragDrop: t('tools.upload.dragDrop'),
    dropHere: t('tools.upload.dropHere'),
    maxSize: t('tools.upload.maxSize', { size: maxSizeMB }),
  }), [t, maxSizeMB]);

  // Prepare styles
  const containerClassName = useMemo(() => cn(
    'relative flex flex-col items-center justify-center',
    'border-2 border-dashed rounded-lg cursor-pointer',
    'transition-colors duration-200',
    'outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
    compact ? 'p-4' : 'p-8',
    isDragging
      ? 'border-primary bg-primary/5'
      : 'border-muted-foreground/25 hover:border-muted-foreground/50',
    disabled && 'opacity-50 cursor-not-allowed pointer-events-none',
    className
  ), [compact, isDragging, disabled, className]);

  const iconClassName = cn('text-muted-foreground mb-2', compact ? 'h-6 w-6' : 'h-10 w-10');
  const textClassName = cn('text-muted-foreground text-center', compact ? 'text-sm' : 'text-base');

  // Handlers
  const handleFiles = useCallback((files: FileList | File[]) => {
    const fileArray = Array.from(files);

    let validFiles = fileArray.filter(file => {
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

    // Enforce single-file selection when multiple is disabled.
    if (!multiple && validFiles.length > 1) {
      validFiles = validFiles.slice(0, 1);
    }

    setRejectedCount(fileArray.length - validFiles.length);

    if (validFiles.length > 0) {
      onFilesSelected?.(validFiles);
      upload(validFiles);
    }
  }, [upload, maxBytes, maxSizeMB, accept, multiple, onFilesSelected]);

  // Build accept MIME types for clipboard paste (e.g. ['image', 'video'] → ['image', 'video'])
  const pasteAcceptTypes = useMemo(
    () => accept.map((assetType) => (assetType === 'document' ? '' : assetType)).filter(Boolean),
    [accept],
  );

  useClipboardPaste({
    enabled: pasteEnabled && !disabled,
    acceptTypes: pasteAcceptTypes.length ? pasteAcceptTypes : undefined,
    maxBytes: maxBytes,
    onFiles: (files) => {
      const toUpload = multiple ? files : files.slice(0, 1);
      onFilesSelected?.(toUpload);
      upload(toUpload);
    },
    onNoMatch: onPasteNoMatch,
  });

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current++;
    if (e.dataTransfer.items?.length) {
      setIsDragging(true);
    }
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;
    if (dragCounter.current === 0) {
      setIsDragging(false);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current = 0;
    setIsDragging(false);

    if (!disabled && e.dataTransfer.files?.length) {
      handleFiles(e.dataTransfer.files);
    }
  }, [disabled, handleFiles]);

  const handleClick = useCallback(() => {
    if (!disabled) {
      inputRef.current?.click();
    }
  }, [disabled]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (disabled) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      inputRef.current?.click();
    }
  }, [disabled]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      handleFiles(e.target.files);
    }
    e.target.value = '';
  }, [handleFiles]);

  // Prepare content
  const displayText = isDragging ? labels.dropHere : labels.dragDrop;
  const showMaxSize = !compact;

  // Announce drag/rejection state to assistive tech.
  const liveMessage = isDragging
    ? labels.dropHere
    : rejectedCount > 0
      ? `${rejectedCount} file(s) were not accepted`
      : '';

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-disabled={disabled || undefined}
      aria-label={labels.dragDrop}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className={containerClassName}
    >
      <input
        ref={inputRef}
        type="file"
        accept={acceptString}
        multiple={multiple}
        onChange={handleInputChange}
        className="hidden"
        tabIndex={-1}
        aria-hidden="true"
        disabled={disabled}
      />

      {children || (
        <>
          <Upload className={iconClassName} aria-hidden="true" />
          <p className={textClassName}>{displayText}</p>
          {showMaxSize && (
            <p className="text-xs text-muted-foreground/60 mt-1">{labels.maxSize}</p>
          )}
          {rejectedCount > 0 && !isDragging && (
            <p className="text-xs text-destructive mt-1">
              {rejectedCount} file(s) skipped (size or type)
            </p>
          )}
        </>
      )}

      <span className="sr-only" role="status" aria-live="polite">
        {liveMessage}
      </span>
    </div>
  );
}
