'use client';

import { cn } from '@djangocfg/ui-core/lib';
import { UploadProvider } from '../context';
import { UploadDropzone } from './UploadDropzone';
import { UploadPreviewList } from './UploadPreviewList';
import type { UploaderProps } from '../types';

interface UploaderContentProps {
  accept?: UploaderProps['accept'];
  maxSizeMB?: UploaderProps['maxSizeMB'];
  multiple?: UploaderProps['multiple'];
  compact?: UploaderProps['compact'];
  showPreview?: UploaderProps['showPreview'];
  pasteEnabled?: UploaderProps['pasteEnabled'];
  onPasteNoMatch?: UploaderProps['onPasteNoMatch'];
  className?: UploaderProps['className'];
  dropzoneClassName?: UploaderProps['dropzoneClassName'];
  previewClassName?: UploaderProps['previewClassName'];
  children?: UploaderProps['children'];
}

function UploaderContent({
  accept,
  maxSizeMB,
  multiple,
  compact,
  showPreview,
  pasteEnabled,
  onPasteNoMatch,
  className,
  dropzoneClassName,
  previewClassName,
  children,
}: UploaderContentProps) {
  return (
    <div className={cn('space-y-4', className)}>
      <UploadDropzone
        accept={accept}
        maxSizeMB={maxSizeMB}
        multiple={multiple}
        compact={compact}
        pasteEnabled={pasteEnabled}
        onPasteNoMatch={onPasteNoMatch}
        className={dropzoneClassName}
      >
        {children}
      </UploadDropzone>

      {showPreview !== false && (
        <UploadPreviewList className={previewClassName} />
      )}
    </div>
  );
}

export function Uploader({
  destination = '/api/upload',
  autoUpload = true,
  concurrent = 3,
  headers,
  params,
  inputFieldName = 'file',
  withCredentials,
  method = 'POST',
  ...contentProps
}: UploaderProps) {
  return (
    <UploadProvider
      destination={{ url: destination, headers, params, method }}
      autoUpload={autoUpload}
      concurrent={concurrent > 1}
      maxConcurrent={concurrent}
      inputFieldName={inputFieldName}
      withCredentials={withCredentials}
    >
      <UploaderContent {...contentProps} />
    </UploadProvider>
  );
}
