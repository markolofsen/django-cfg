'use client';

import { useMemo, useCallback } from 'react';
import { X, CheckCircle, AlertCircle, Loader2, FileIcon, ImageIcon, FileAudio, FileVideo, RotateCcw } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';
import {
  Button,
  Progress,
  Badge,
  TooltipHint,
  Skeleton,
} from '@djangocfg/ui-core/components';
import { useT } from '@djangocfg/i18n';
import { formatFileSize, truncateFilename } from '../utils';
import type { UploadPreviewItemProps, AssetType, UploadStatus } from '../types';

const ASSET_ICONS: Record<AssetType, typeof FileIcon> = {
  image: ImageIcon,
  audio: FileAudio,
  video: FileVideo,
  document: FileIcon,
};

const REMOVABLE_STATUSES: UploadStatus[] = ['pending', 'uploading', 'error', 'aborted'];

export function UploadPreviewItem({
  item,
  onRemove,
  onRetry,
  showThumbnail = true,
}: UploadPreviewItemProps) {
  const t = useT();
  const { id, file, status, progress, previewUrl, error } = item;

  // Prepare labels
  const labels = useMemo(() => ({
    uploaded: t('tools.upload.uploaded'),
    failed: t('tools.upload.failed'),
    cancel: t('tools.upload.cancel'),
    pending: t('tools.upload.pending'),
    retry: t('tools.upload.retry'),
    remove: t('tools.upload.remove'),
  }), [t]);

  // Prepare file info
  const assetType = useMemo((): AssetType => {
    if (file.type.startsWith('image/')) return 'image';
    if (file.type.startsWith('audio/')) return 'audio';
    if (file.type.startsWith('video/')) return 'video';
    return 'document';
  }, [file.type]);

  const fileSize = useMemo(() => formatFileSize(file.size), [file.size]);
  const shortName = useMemo(() => truncateFilename(file.name), [file.name]);
  const progressPercent = Math.round(progress);

  // Prepare visibility flags
  const Icon = ASSET_ICONS[assetType];
  const canShowImagePreview = showThumbnail && !!previewUrl && assetType === 'image';
  const canShowVideoPreview = showThumbnail && !!previewUrl && assetType === 'video';
  const canRetry = (status === 'error' || status === 'aborted') && !!onRetry;
  const canRemove = REMOVABLE_STATUSES.includes(status) && !!onRemove;
  const isUploading = status === 'uploading';
  const hasError = !!error;

  // Prepare styles
  const containerClassName = cn(
    'flex items-center gap-3 p-3 rounded-lg border',
    'bg-card',
    hasError && 'border-destructive/50'
  );

  // Prepare tooltip label for remove button
  const removeTooltip = isUploading ? labels.cancel : labels.remove;

  // Handlers
  const handleRemove = useCallback(() => {
    onRemove?.(id);
  }, [id, onRemove]);

  const handleRetry = useCallback(() => {
    onRetry?.(id);
  }, [id, onRetry]);

  // Prepare status badge
  const statusBadge = useMemo(() => {
    switch (status) {
      case 'uploading':
        return (
          <Badge variant="secondary" className="gap-1 tabular-nums">
            <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" />
            {progressPercent}%
          </Badge>
        );
      case 'complete':
        return (
          <Badge variant="default" className="gap-1 bg-success text-success-foreground border-transparent">
            <CheckCircle className="h-3 w-3" aria-hidden="true" />
            {labels.uploaded}
          </Badge>
        );
      case 'error':
        return (
          <Badge variant="destructive" className="gap-1">
            <AlertCircle className="h-3 w-3" aria-hidden="true" />
            {labels.failed}
          </Badge>
        );
      case 'aborted':
        return (
          <Badge variant="secondary" className="gap-1">
            {labels.cancel}
          </Badge>
        );
      default:
        return (
          <Badge variant="outline">
            {labels.pending}
          </Badge>
        );
    }
  }, [status, progressPercent, labels]);

  // Prepare thumbnail content
  const thumbnailContent = useMemo(() => {
    if (canShowImagePreview && previewUrl) {
      return <img src={previewUrl} alt={file.name} className="w-full h-full object-cover" />;
    }
    if (canShowVideoPreview && previewUrl) {
      return (
        <video
          src={previewUrl}
          className="w-full h-full object-cover"
          muted
          playsInline
          preload="metadata"
          aria-label={file.name}
        />
      );
    }
    if (showThumbnail && !previewUrl && (assetType === 'image' || assetType === 'video')) {
      return <Skeleton className="w-full h-full" />;
    }
    return <Icon className="h-6 w-6 text-muted-foreground" aria-hidden="true" />;
  }, [canShowImagePreview, canShowVideoPreview, showThumbnail, previewUrl, assetType, file.name, Icon]);

  return (
    <div className={containerClassName}>
      {/* Thumbnail / Icon */}
      <div className="flex-shrink-0 w-12 h-12 rounded-md overflow-hidden bg-muted flex items-center justify-center">
        {thumbnailContent}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <TooltipHint
          tooltip={
            shortName !== file.name
              ? { content: <span className="block max-w-xs break-all">{file.name}</span>, side: 'top' }
              : undefined
          }
        >
          <p className="text-sm font-medium cursor-default leading-tight">
            {shortName}
          </p>
        </TooltipHint>

        <p className="text-xs text-muted-foreground tabular-nums">{fileSize}</p>

        {isUploading && (
          <Progress
            value={progressPercent}
            className="h-1 mt-1"
            aria-label={`${progressPercent}%`}
          />
        )}

        {hasError && (
          <TooltipHint
            tooltip={{ content: <span className="block max-w-xs break-all">{error}</span>, side: 'bottom' }}
          >
            <p className="text-xs text-destructive mt-1 truncate cursor-default">{error}</p>
          </TooltipHint>
        )}
      </div>

      {/* Status & Actions */}
      <div className="flex items-center gap-2">
        {statusBadge}

        {canRetry && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={handleRetry}
            aria-label={labels.retry}
            tooltip={labels.retry}
          >
            <RotateCcw className="h-4 w-4" aria-hidden="true" />
          </Button>
        )}

        {canRemove && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={handleRemove}
            aria-label={removeTooltip}
            tooltip={removeTooltip}
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </Button>
        )}
      </div>
    </div>
  );
}
