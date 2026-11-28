export type AssetType = 'image' | 'audio' | 'video' | 'document';

export type UploadStatus =
  | 'pending'
  | 'uploading'
  | 'complete'
  | 'error'
  | 'aborted';

export interface UploadedAsset {
  id: string;
  name: string;
  type: AssetType;
  url: string;
  thumbnailUrl?: string;
  size: number;
  mimeType: string;
  duration?: number;
}

export interface UploadItem {
  id: string;
  file: File;
  status: UploadStatus;
  progress: number;
  previewUrl?: string;
  asset?: UploadedAsset;
  error?: string;
}

export interface UploaderProps {
  /** Upload destination URL */
  destination?: string;
  /** Allowed asset types (default: all) */
  accept?: AssetType[];
  /** Max file size in MB (default: 100) */
  maxSizeMB?: number;
  /** Allow multiple files (default: true) */
  multiple?: boolean;
  /** Auto-upload on file add (default: true) */
  autoUpload?: boolean;
  /** Show preview list (default: true) */
  showPreview?: boolean;
  /** Enable Ctrl+V / Cmd+V paste-to-upload (default: true) */
  pasteEnabled?: boolean;
  /** Called when paste fires but no uploadable content was found */
  onPasteNoMatch?: () => void;
  /** Compact mode (smaller dropzone) */
  compact?: boolean;
  /** Max concurrent uploads (default: 3) */
  concurrent?: number;
  /** Custom headers for upload request */
  headers?: Record<string, string>;
  /** Additional form data to send */
  params?: Record<string, unknown>;
  /** Field name for file (default: 'file') */
  inputFieldName?: string;
  /** Send cookies with request (default: true for same-origin) */
  withCredentials?: boolean;
  /** HTTP method (default: 'POST') */
  method?: string;

  // Callbacks
  onFileAdded?: (file: File) => void;
  onUploadStart?: (item: UploadItem) => void;
  onUploadProgress?: (item: UploadItem) => void;
  /** Called on successful upload. rawResponse contains the original API response. */
  onUploadComplete?: (asset: UploadedAsset, rawResponse: Record<string, unknown>) => void;
  /** Called on upload error. rawResponse contains the original error response (if any). */
  onUploadError?: (error: string, file: File, rawResponse: Record<string, unknown> | null) => void;
  onBatchComplete?: (assets: UploadedAsset[]) => void;

  // Styling
  className?: string;
  dropzoneClassName?: string;
  previewClassName?: string;
  children?: React.ReactNode;
}

export interface UploadDropzoneProps {
  accept?: AssetType[];
  multiple?: boolean;
  maxSizeMB?: number;
  compact?: boolean;
  disabled?: boolean;
  className?: string;
  children?: React.ReactNode;
  /** Called with validated files on drop/click/paste */
  onFilesSelected?: (files: File[]) => void;
  /**
   * Custom upload function. If provided, rpldy upload is skipped — files go only here.
   * Use this when you handle uploads yourself (e.g. custom API hooks).
   * Requires no UploadProvider ancestor.
   */
  uploadFn?: (files: File[]) => void;
  /** Enable Ctrl+V / Cmd+V paste-to-upload (default: true) */
  pasteEnabled?: boolean;
  /** Called when paste fires but no uploadable content was found */
  onPasteNoMatch?: () => void;
}

export interface UploadPreviewListProps {
  className?: string;
  onRemove?: (id: string) => void;
  onRetry?: (id: string) => void;
  showThumbnails?: boolean;
  showProgress?: boolean;
}

export interface UploadPreviewItemProps {
  item: UploadItem;
  onRemove?: (id: string) => void;
  onRetry?: (id: string) => void;
  showThumbnail?: boolean;
}
