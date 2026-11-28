"use client"

/**
 * Base64 Encoding/Decoding Hook
 *
 * Provides base64 encoding/decoding with dev mode detection:
 * - In production: encodes data to base64
 * - In development: returns data as-is (no encoding)
 */

import { isDev } from '../utils/env';

/**
 * Encode string to base64
 * @param data - String data to encode
 * @returns Base64 encoded string (or original in dev mode)
 */
export function encodeBase64(data: string): string {
  if (isDev) {
    return data;
  }

  try {
    // Browser-safe base64 encoding
    if (typeof window !== 'undefined') {
      return btoa(encodeURIComponent(data).replace(/%([0-9A-F]{2})/g, (_, p1) => {
        return String.fromCharCode(parseInt(p1, 16));
      }));
    }
    // Node.js fallback
    return Buffer.from(data, 'utf-8').toString('base64');
  } catch (error) {
    console.error('Base64 encoding error:', error);
    return data; // Return original on error
  }
}

/**
 * Decode base64 to string
 * @param encoded - Base64 encoded string
 * @returns Decoded string (or original in dev mode)
 */
export function decodeBase64(encoded: string): string {
  if (isDev) {
    return encoded;
  }

  try {
    // Browser-safe base64 decoding
    if (typeof window !== 'undefined') {
      const binary = atob(encoded);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }
      return decodeURIComponent(
        Array.from(bytes)
          .map(byte => '%' + ('00' + byte.toString(16)).slice(-2))
          .join('')
      );
    }
    // Node.js fallback
    return Buffer.from(encoded, 'base64').toString('utf-8');
  } catch (error) {
    console.error('Base64 decoding error:', error);
    return encoded; // Return original on error
  }
}

/**
 * Hook for base64 encoding/decoding
 * @returns Object with encode and decode functions
 */
export function useBase64() {
  return {
    encode: encodeBase64,
    decode: decodeBase64,
    isDev,
  };
}
