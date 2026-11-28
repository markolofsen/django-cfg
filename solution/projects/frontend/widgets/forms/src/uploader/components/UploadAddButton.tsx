'use client';

import { useCallback, useRef, useMemo } from 'react';
import { useUploady } from '@rpldy/uploady';
import { Plus } from 'lucide-react';
import { Button } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { useT } from '@djangocfg/i18n';
import { buildAcceptString, getAssetTypeFromMime, logger } from '../utils';
import type { AssetType } from '../types';

interface UploadAddButtonProps {
  accept?: AssetType[];
  multiple?: boolean;
  maxSizeMB?: number;
  disabled?: boolean;
  className?: string;
  variant?: 'default' | 'outline' | 'ghost' | 'secondary';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  children?: React.ReactNode;
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

export function UploadAddButton({
  accept = ['image', 'audio', 'video', 'document'],
  multiple = true,
  maxSizeMB = 100,
  disabled = false,
  className,
  variant = 'outline',
  size = 'default',
  children,
}: UploadAddButtonProps) {
  const t = useT();
  const { upload } = useUploady();
  const inputRef = useRef<HTMLInputElement>(null);

  const acceptString = useMemo(() => buildAcceptString(accept), [accept]);

  const handleFiles = useCallback((files: FileList | File[]) => {
    const fileArray = Array.from(files);
    const maxBytes = maxSizeMB * 1024 * 1024;

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

    if (validFiles.length > 0) {
      upload(validFiles);
    }
  }, [upload, maxSizeMB, accept, multiple]);

  const handleClick = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      handleFiles(e.target.files);
    }
    e.target.value = '';
  }, [handleFiles]);

  return (
    <>
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
      <Button
        variant={variant}
        size={size}
        disabled={disabled}
        onClick={handleClick}
        className={cn(className)}
      >
        {children || (
          <>
            <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
            {t('tools.upload.upload')}
          </>
        )}
      </Button>
    </>
  );
}
