import type { AssetType } from '../types';

export const MIME_TO_ASSET_TYPE: Record<string, AssetType> = {
  // Images
  'image/jpeg': 'image',
  'image/png': 'image',
  'image/gif': 'image',
  'image/webp': 'image',
  'image/svg+xml': 'image',
  'image/avif': 'image',

  // Audio
  'audio/mpeg': 'audio',
  'audio/wav': 'audio',
  'audio/ogg': 'audio',
  'audio/webm': 'audio',
  'audio/aac': 'audio',
  'audio/flac': 'audio',

  // Video
  'video/mp4': 'video',
  'video/webm': 'video',
  'video/ogg': 'video',
  'video/quicktime': 'video',
  'video/x-msvideo': 'video',

  // Documents
  'application/pdf': 'document',
  'application/msword': 'document',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document',
  'application/vnd.ms-excel': 'document',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'document',
  'text/plain': 'document',
  'text/csv': 'document',
  'application/json': 'document',
};

export const ASSET_TYPE_ACCEPT: Record<AssetType, string[]> = {
  image: ['image/*'],
  audio: ['audio/*'],
  video: ['video/*'],
  document: [
    'application/pdf',
    '.doc', '.docx',
    '.xls', '.xlsx',
    '.txt', '.csv',
    'application/json',
  ],
};

export function getAssetTypeFromMime(mimeType: string): AssetType {
  return MIME_TO_ASSET_TYPE[mimeType] || 'document';
}

export function buildAcceptString(types: AssetType[]): string {
  const accepts = types.flatMap(type => ASSET_TYPE_ACCEPT[type]);
  return accepts.join(',');
}
