import type { ApiKey } from '../types';
import { HTTP_METHOD_COLORS, HTTP_STATUS_COLORS } from '../constants';

export const getMethodColor = (
  method: string
): 'success' | 'primary' | 'warning' | 'error' | 'default' => {
  return HTTP_METHOD_COLORS[method.toUpperCase() as keyof typeof HTTP_METHOD_COLORS] || 'default';
};

export const getStatusColor = (
  status: number
): 'success' | 'warning' | 'error' | 'default' => {
  const firstDigit = Math.floor(status / 100).toString();
  return HTTP_STATUS_COLORS[firstDigit as keyof typeof HTTP_STATUS_COLORS] || 'default';
};

export const formatApiKeyDisplay = (apiKey: ApiKey): string => {
  const preview = apiKey.id.substring(0, 8);
  return `${apiKey.name} (${preview}...)`;
};

export const isValidJson = (str: string): boolean => {
  if (!str || typeof str !== 'string') return false;
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
};

export const formatRequestHeaders = (headers: Record<string, string>): string => {
  return JSON.stringify(headers, null, 2);
};

export const parseRequestHeaders = (headersString: string): Record<string, string> => {
  if (!headersString || typeof headersString !== 'string') {
    return { 'Content-Type': 'application/json' };
  }

  try {
    const parsed = JSON.parse(headersString);
    return typeof parsed === 'object' && parsed !== null ? parsed : { 'Content-Type': 'application/json' };
  } catch {
    return { 'Content-Type': 'application/json' };
  }
};

// URL helpers moved to ./url.ts — keep this file focused on non-URL
// formatters (method/status colour maps, JSON validation, header parsing).
