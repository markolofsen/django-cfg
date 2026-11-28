import type { UploadedAsset } from '../types';
import { getAssetTypeFromMime } from './assetTypes';

type ResponseTransformer = (
  response: Record<string, unknown>,
  file: File
) => Partial<UploadedAsset>;

type ErrorTransformer = (
  response: Record<string, unknown> | null,
  status: number
) => string;

/**
 * Default response transformer.
 * Supports common API response formats:
 * - { id, url, thumbnail_url, duration }
 * - { id, file, thumbnail, duration }
 * - { id, file_url, thumb_url }
 */
export const defaultResponseTransformer: ResponseTransformer = (response, _file) => {
  const data = response as Record<string, unknown>;

  return {
    id: (data.id as string) || (data.uuid as string) || undefined,
    url: (data.url as string) || (data.file as string) || (data.file_url as string) || '',
    thumbnailUrl: (data.thumbnail_url as string) || (data.thumbnail as string) || (data.thumb_url as string) || (data.preview_url as string),
    duration: (data.duration as number) || undefined,
  };
};

/**
 * Default error transformer.
 * Supports common API error formats:
 * - { message: "..." }
 * - { error: "..." }
 * - { detail: "..." }
 * - { errors: { file: ["..."] } }
 * - { file: ["..."] }
 * - { non_field_errors: ["..."] }
 */
export const defaultErrorTransformer: ErrorTransformer = (response, status) => {
  if (!response) {
    if (status === 0) return 'Network error';
    if (status === 413) return 'File too large';
    if (status === 415) return 'Unsupported file type';
    if (status === 401) return 'Unauthorized';
    if (status === 403) return 'Forbidden';
    if (status >= 500) return 'Server error';
    return `Upload failed (${status})`;
  }

  const data = response as Record<string, unknown>;

  // Simple message field
  if (typeof data.message === 'string') return data.message;
  if (typeof data.error === 'string') return data.error;
  if (typeof data.detail === 'string') return data.detail;

  // Django REST Framework validation errors
  if (data.file && Array.isArray(data.file) && data.file.length > 0) {
    return data.file[0] as string;
  }
  if (data.non_field_errors && Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
    return data.non_field_errors[0] as string;
  }

  // Nested errors object
  if (data.errors && typeof data.errors === 'object') {
    const errors = data.errors as Record<string, unknown>;
    const firstKey = Object.keys(errors)[0];
    if (firstKey) {
      const fieldErrors = errors[firstKey];
      if (Array.isArray(fieldErrors) && fieldErrors.length > 0) {
        return `${firstKey}: ${fieldErrors[0]}`;
      }
    }
  }

  return 'Upload failed';
};

/**
 * Build complete UploadedAsset from response and file.
 */
export function buildAssetFromResponse(
  response: Record<string, unknown>,
  file: File,
  transformer: ResponseTransformer = defaultResponseTransformer
): UploadedAsset {
  const partial = transformer(response, file);

  return {
    id: partial.id || crypto.randomUUID(),
    name: file.name,
    type: getAssetTypeFromMime(file.type),
    url: partial.url || '',
    thumbnailUrl: partial.thumbnailUrl,
    size: file.size,
    mimeType: file.type,
    duration: partial.duration,
  };
}

/**
 * Extract error message from response.
 */
export function extractErrorMessage(
  response: Record<string, unknown> | null,
  status: number,
  transformer: ErrorTransformer = defaultErrorTransformer
): string {
  return transformer(response, status);
}
