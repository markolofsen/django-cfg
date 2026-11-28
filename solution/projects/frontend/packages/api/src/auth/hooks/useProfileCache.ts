"use client"

/**
 * Profile Cache Hook
 *
 * Provides localStorage-based caching for user profile with:
 * - TTL (Time To Live) - default 1 hour
 * - Version control for migrations
 * - Automatic invalidation on expiry
 */

import type { User } from '../../';
import { authLogger as profileLogger } from '../utils/logger';
import { CFG_KEYS } from '../../runtime/keys';
import { decodeBase64, encodeBase64 } from './useBase64';

// Cache configuration
const CACHE_KEY = CFG_KEYS.profileCache.key;
const CACHE_VERSION = 1;
const DEFAULT_TTL = 14400000; // 4 hours in milliseconds (reduced API calls, more resilient)

export interface ProfileCacheOptions {
  /** Time to live in milliseconds (default: 1 hour) */
  ttl?: number;
}

interface CachedProfile {
  version: number;
  data: User;
  timestamp: number;
  ttl: number;
}

/**
 * Get cached profile from localStorage
 * @returns User profile if valid cache exists, null otherwise
 */
export function getCachedProfile(): User | null {
  try {
    if (typeof window === 'undefined') return null;

    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) {
      profileLogger.debug('No cached profile found');
      return null;
    }

    // Decode from base64
    const decoded = decodeBase64(cached);
    const cachedData: CachedProfile = JSON.parse(decoded);

    // Version check
    if (cachedData.version !== CACHE_VERSION) {
      profileLogger.warn('Cache version mismatch, clearing cache');
      clearProfileCache();
      return null;
    }

    // TTL check
    const now = Date.now();
    const age = now - cachedData.timestamp;
    if (age > cachedData.ttl) {
      profileLogger.info('Cache expired, clearing');
      clearProfileCache();
      return null;
    }

    profileLogger.debug('Cache hit, age:', Math.round(age / 1000), 'seconds');
    return cachedData.data;
  } catch (error) {
    profileLogger.error('Error reading cache:', error);
    clearProfileCache();
    return null;
  }
}

/**
 * Save profile to localStorage cache
 * @param profile - User profile to cache
 * @param options - Cache options (TTL)
 */
export function setCachedProfile(profile: User, options?: ProfileCacheOptions): void {
  try {
    if (typeof window === 'undefined') return;

    const cachedData: CachedProfile = {
      version: CACHE_VERSION,
      data: profile,
      timestamp: Date.now(),
      ttl: options?.ttl || DEFAULT_TTL,
    };

    // Encode to base64
    const encoded = encodeBase64(JSON.stringify(cachedData));
    localStorage.setItem(CACHE_KEY, encoded);
    profileLogger.debug('Profile cached, TTL:', cachedData.ttl / 1000, 'seconds');
  } catch (error) {
    profileLogger.error('Error writing cache:', error);
  }
}

/**
 * Clear profile cache from localStorage
 */
export function clearProfileCache(): void {
  try {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(CACHE_KEY);
    profileLogger.debug('Cache cleared');
  } catch (error) {
    profileLogger.error('Error clearing cache:', error);
  }
}

/**
 * Check if cached profile is valid (exists and not expired)
 */
export function hasValidCache(): boolean {
  return getCachedProfile() !== null;
}

/**
 * Get cache metadata (age, TTL, etc.)
 */
export function getCacheMetadata(): {
  exists: boolean;
  age?: number;
  ttl?: number;
  expiresIn?: number;
} | null {
  try {
    if (typeof window === 'undefined') return null;

    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return { exists: false };

    // Decode from base64
    const decoded = decodeBase64(cached);
    const cachedData: CachedProfile = JSON.parse(decoded);
    const now = Date.now();
    const age = now - cachedData.timestamp;
    const expiresIn = cachedData.ttl - age;

    return {
      exists: true,
      age,
      ttl: cachedData.ttl,
      expiresIn: Math.max(0, expiresIn),
    };
  } catch (error) {
    profileLogger.error('Error reading metadata:', error);
    return null;
  }
}
