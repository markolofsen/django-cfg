"use client"

/**
 * cURL Generator
 *
 * Generates cURL commands from API request details with authentication token
 */

import { auth } from '@djangocfg/api';
import consola from 'consola';

export interface CurlOptions {
  method: string;
  path: string;
  token?: string;
  body?: unknown;
  headers?: Record<string, string>;
  baseUrl?: string;
  queryParams?: Record<string, string>;
}

/**
 * Get the current access token via the shared auth store.
 *
 * Must go through `auth.getToken()` — it reads the live token from whichever
 * backend the app configured (localStorage *or* cookie) under the canonical
 * `cfg.auth.access_token` key. Reading raw localStorage keys here (the old
 * `access_token`/`token`/`auth_token` guesses) never matched and always
 * returned null, so the copied cURL had no Authorization header.
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;

  try {
    return auth.getToken();
  } catch (error) {
    consola.error('Failed to get auth token:', error);
    return null;
  }
}

/**
 * Format headers for cURL command
 */
function formatHeaders(headers: Record<string, string>): string[] {
  return Object.entries(headers).map(
    ([key, value]) => `-H '${key}: ${value}'`
  );
}

/**
 * Escape single quotes in string for shell
 */
function escapeShell(str: string): string {
  return str.replace(/'/g, "'\\''");
}

/**
 * Generate cURL command from request details
 */
export function generateCurl(options: CurlOptions): string {
  const {
    method,
    path,
    token = getAuthToken() || undefined,  // Auto-fetch if not provided
    body,
    headers = {},
    baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  } = options;

  const curlParts: string[] = ['curl'];

  // Build URL
  const url = `${baseUrl}${path}`;
  curlParts.push(`'${url}'`);

  // Add method if not GET
  if (method.toUpperCase() !== 'GET') {
    curlParts.push(`-X ${method.toUpperCase()}`);
  }

  // Default headers
  const allHeaders: Record<string, string> = {
    'Accept': '*/*',
    'Content-Type': 'application/json',
    ...headers,
  };

  if (token) {
    allHeaders['Authorization'] = `Bearer ${token}`;
  }

  // Add all headers
  const headerStrings = formatHeaders(allHeaders);
  curlParts.push(...headerStrings);

  // Add body for non-GET requests
  if (body && method.toUpperCase() !== 'GET') {
    const bodyJson = typeof body === 'string'
      ? body
      : JSON.stringify(body, null, 2);
    curlParts.push(`-d '${escapeShell(bodyJson)}'`);
  }

  // Join with line continuation
  return curlParts.join(' \\\n  ');
}

/**
 * Generate cURL from validation error details
 * Auto-fetches token from localStorage
 */
export function generateCurlFromError(detail: {
  method: string;
  path: string;
  response?: unknown;
}): string {
  return generateCurl({
    method: detail.method,
    path: detail.path,
    // token is auto-fetched in generateCurl
  });
}
