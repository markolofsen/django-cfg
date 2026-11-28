/**
 * API Key Management Utility
 *
 * Provides centralized functions for managing API keys in headers and requests.
 * This utility can be used across different components that need to handle API keys.
 */

import type { ApiKey } from '../types';

export type { ApiKey };

export interface HeadersWithApiKey {
  [key: string]: string;
}

/**
 * Add API key to request headers
 * @param headers - Existing headers object
 * @param apiKey - API key object or string
 * @returns Headers with API key added
 */
export function addApiKeyToHeaders(headers: HeadersWithApiKey, apiKey: ApiKey | string | null): HeadersWithApiKey {
  if (!apiKey) {
    return headers;
  }

  // ``secret`` is the raw key that goes in the X-API-Key header.
  // Falls back to ``id`` for backwards compatibility — older callers
  // only had ``id`` and used it as both selector and secret.
  const keyValue = typeof apiKey === 'string' ? apiKey : (apiKey.secret || apiKey.id || '');

  return {
    ...headers,
    'X-API-Key': keyValue,
  };
}

/**
 * Remove API key from headers object
 * @param headers - Headers object
 * @returns Headers without API key
 */
export function removeApiKeyFromHeaders(headers: HeadersWithApiKey): HeadersWithApiKey {
  const { 'X-API-Key': _removed, ...remainingHeaders } = headers;
  return remainingHeaders;
}

/**
 * Remove API key from headers JSON string
 * @param headersJson - JSON string of headers
 * @returns JSON string without API key
 */
export function removeApiKeyFromHeadersJson(headersJson: string): string {
  try {
    const headers = JSON.parse(headersJson);
    const updatedHeaders = removeApiKeyFromHeaders(headers);
    return JSON.stringify(updatedHeaders, null, 2);
  } catch (error) {
    console.error('Error parsing headers JSON:', error);
    return headersJson;
  }
}

/**
 * Update headers JSON string with API key
 * @param headersJson - JSON string of headers
 * @param apiKey - API key object or string
 * @returns Updated JSON string
 */
export function updateHeadersJsonWithApiKey(headersJson: string, apiKey: ApiKey | string | null): string {
  try {
    const headers = JSON.parse(headersJson);
    const updatedHeaders = addApiKeyToHeaders(headers, apiKey);
    return JSON.stringify(updatedHeaders, null, 2);
  } catch (error) {
    console.error('Error parsing headers JSON:', error);
    return headersJson;
  }
}

/**
 * Find API key by ID in a list of API keys
 * @param apiKeys - Array of API keys
 * @param keyId - ID of the API key to find
 * @returns API key object or null
 */
export function findApiKeyById(apiKeys: ApiKey[], keyId: string): ApiKey | null {
  return apiKeys.find((key) => key.id === keyId) || null;
}

/**
 * Validate API key format
 * @param apiKey - API key string to validate
 * @returns Whether the API key format is valid
 */
export function validateApiKeyFormat(apiKey: string): boolean {
  // Basic validation - adjust based on your API key format requirements
  return typeof apiKey === 'string' && apiKey.length > 0 && apiKey.trim() !== '';
}

/**
 * Create default headers with API key
 * @param apiKey - API key object or string
 * @returns Default headers with API key
 */
export function createDefaultHeaders(apiKey?: ApiKey | string): HeadersWithApiKey {
  const defaultHeaders: HeadersWithApiKey = {
    'Content-Type': 'application/json',
  };

  if (apiKey) {
    return addApiKeyToHeaders(defaultHeaders, apiKey);
  }

  return defaultHeaders;
}

/**
 * Merge headers with API key
 * @param baseHeaders - Base headers object
 * @param additionalHeaders - Additional headers to merge
 * @param apiKey - API key to add
 * @returns Merged headers with API key
 */
export function mergeHeadersWithApiKey(baseHeaders: HeadersWithApiKey, additionalHeaders: HeadersWithApiKey, apiKey?: ApiKey | string): HeadersWithApiKey {
  const mergedHeaders = { ...baseHeaders, ...additionalHeaders };

  if (apiKey) {
    return addApiKeyToHeaders(mergedHeaders, apiKey);
  }

  return mergedHeaders;
}

/**
 * Log API key usage (for debugging/analytics)
 * @param apiKey - API key that was used
 * @param endpoint - Endpoint that was called
 * @param success - Whether the request was successful
 */
export function logApiKeyUsage(apiKey: ApiKey | string, endpoint: string, success: boolean): void {
  const keyValue = typeof apiKey === 'string' ? apiKey : (apiKey.secret || apiKey.id || '');
  const keyName = typeof apiKey === 'string' ? 'Unknown' : apiKey.name;

  console.log(`API Key Usage:`, {
    keyName,
    keyValue: keyValue.substring(0, 8) + '...',
    endpoint,
    success,
    timestamp: new Date().toISOString(),
  });
}
