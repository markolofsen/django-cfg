/**
 * JWT Token Helper Utilities
 *
 * Provides utilities for decoding and validating JWT tokens
 * without requiring external dependencies.
 */

interface JWTPayload {
  exp?: number;
  iat?: number;
  user_id?: string | number;
  [key: string]: any;
}

/**
 * Decode JWT token without verification
 *
 * WARNING: This only decodes the token, it does NOT verify the signature!
 * Only use for debugging and checking expiry.
 *
 * @param token - JWT token string
 * @returns Decoded payload or null if invalid
 */
export function decodeJWT(token: string): JWTPayload | null {
  try {
    // JWT format: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    // Decode the payload (second part)
    const payload = parts[1];

    // Base64 URL decode
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Failed to decode JWT:', error);
    return null;
  }
}

/**
 * Check if JWT token is expired
 *
 * @param token - JWT token string
 * @returns true if expired, false if valid, null if cannot decode
 */
export function isTokenExpired(token: string): boolean | null {
  const payload = decodeJWT(token);
  if (!payload || !payload.exp) {
    return null;
  }

  // exp is in seconds, Date.now() is in milliseconds
  const expiryTime = payload.exp * 1000;
  const now = Date.now();

  return now >= expiryTime;
}

/**
 * Get token expiry time
 *
 * @param token - JWT token string
 * @returns Expiry date or null if cannot decode
 */
export function getTokenExpiry(token: string): Date | null {
  const payload = decodeJWT(token);
  if (!payload || !payload.exp) {
    return null;
  }

  return new Date(payload.exp * 1000);
}

/**
 * Get time until token expires
 *
 * @param token - JWT token string
 * @returns Milliseconds until expiry, or null if cannot decode
 */
export function getTimeUntilExpiry(token: string): number | null {
  const expiry = getTokenExpiry(token);
  if (!expiry) {
    return null;
  }

  return expiry.getTime() - Date.now();
}

/**
 * Mask JWT token for safe logging
 * Shows first 10 and last 6 characters
 *
 * @param token - JWT token string
 * @returns Masked token
 */
export function maskToken(token: string): string {
  if (!token || token.length < 20) {
    return '***';
  }

  const start = token.substring(0, 10);
  const end = token.substring(token.length - 6);

  return `${start}...${end}`;
}

/**
 * Get token info for debugging
 *
 * @param token - JWT token string
 * @returns Object with token information
 */
export function getTokenInfo(token: string) {
  const payload = decodeJWT(token);
  const expiry = getTokenExpiry(token);
  const timeUntilExpiry = getTimeUntilExpiry(token);
  const isExpired = isTokenExpired(token);

  return {
    masked: maskToken(token),
    payload,
    expiry,
    timeUntilExpiry,
    isExpired,
    expiryFormatted: expiry ? expiry.toLocaleString() : 'unknown',
    timeUntilExpiryFormatted: timeUntilExpiry
      ? `${Math.floor(timeUntilExpiry / 1000)}s`
      : 'unknown',
  };
}
