// @vitest-environment jsdom
/**
 * Tests for useTwoFactorStatus hook
 *
 * Tests the hook for checking and managing 2FA status in ProfileLayout.
 * (Migrated from Jest to Vitest: jest.* → vi.*, added jsdom env + vi import.)
 */

import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useTwoFactorStatus } from '../hooks/useTwoFactorStatus';

// Mock the Orval endpoint functions the hook calls directly.
const mockDevicesRetrieve = vi.fn();
const mockDisableCreate = vi.fn();

vi.mock('../../_api/endpoints', () => ({
  cfgTotpDevicesRetrieve: () => mockDevicesRetrieve(),
  cfgTotpDisableCreate: (args: unknown) => mockDisableCreate(args),
}));

vi.mock('../utils/logger', () => ({
  authLogger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

describe('useTwoFactorStatus', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('initial state', () => {
    it('should initialize with null has2FAEnabled', () => {
      const { result } = renderHook(() => useTwoFactorStatus());

      expect(result.current.has2FAEnabled).toBeNull();
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.devices).toEqual([]);
    });
  });

  describe('fetchStatus', () => {
    it('should fetch 2FA status successfully when enabled', async () => {
      mockDevicesRetrieve.mockResolvedValue({
          has_2fa_enabled: true,
          devices: [
            {
              id: '123',
              name: 'My Authenticator',
              created_at: '2024-01-01T00:00:00Z',
              last_used_at: '2024-01-02T00:00:00Z',
              is_primary: true,
            },
          ],
      });

      const { result } = renderHook(() => useTwoFactorStatus());

      await act(async () => {
        await result.current.fetchStatus();
      });

      expect(result.current.has2FAEnabled).toBe(true);
      expect(result.current.devices).toHaveLength(1);
      expect(result.current.devices[0]).toEqual({
        id: '123',
        name: 'My Authenticator',
        createdAt: '2024-01-01T00:00:00Z',
        lastUsedAt: '2024-01-02T00:00:00Z',
        isPrimary: true,
      });
      expect(result.current.error).toBeNull();
    });

    it('should fetch 2FA status successfully when disabled', async () => {
      mockDevicesRetrieve.mockResolvedValue({
          has_2fa_enabled: false,
          devices: [],
      });

      const { result } = renderHook(() => useTwoFactorStatus());

      await act(async () => {
        await result.current.fetchStatus();
      });

      expect(result.current.has2FAEnabled).toBe(false);
      expect(result.current.devices).toEqual([]);
      expect(result.current.error).toBeNull();
    });

    it('should handle fetch error', async () => {
      mockDevicesRetrieve.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useTwoFactorStatus());

      await act(async () => {
        await result.current.fetchStatus();
      });

      expect(result.current.error).toBe('Network error');
      expect(result.current.has2FAEnabled).toBeNull();
    });

    it('should set loading state during fetch', async () => {
      let resolvePromise: (value: unknown) => void;
      mockDevicesRetrieve.mockReturnValue(
        new Promise((resolve) => {
          resolvePromise = resolve;
        })
      );

      const { result } = renderHook(() => useTwoFactorStatus());

      // Start fetch
      let fetchPromise: Promise<void>;
      act(() => {
        fetchPromise = result.current.fetchStatus();
      });

      // Should be loading
      expect(result.current.isLoading).toBe(true);

      // Resolve
      await act(async () => {
        resolvePromise!({ has_2fa_enabled: true, devices: [] });
        await fetchPromise;
      });

      // Should not be loading
      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('disable2FA', () => {
    it('should disable 2FA successfully', async () => {
      mockDisableCreate.mockResolvedValue({ message: '2FA disabled' });

      const { result } = renderHook(() => useTwoFactorStatus());

      // Set initial state
      await act(async () => {
        mockDevicesRetrieve.mockResolvedValue({ has_2fa_enabled: true, devices: [] });
        await result.current.fetchStatus();
      });

      expect(result.current.has2FAEnabled).toBe(true);

      // Disable 2FA
      let success: boolean;
      await act(async () => {
        success = await result.current.disable2FA('123456');
      });

      expect(success!).toBe(true);
      expect(result.current.has2FAEnabled).toBe(false);
      expect(result.current.devices).toEqual([]);
      expect(mockDisableCreate).toHaveBeenCalledWith({ code: '123456' });
    });

    it('should reject invalid code format', async () => {
      const { result } = renderHook(() => useTwoFactorStatus());

      // Try with short code
      let success: boolean;
      await act(async () => {
        success = await result.current.disable2FA('12345');
      });

      expect(success!).toBe(false);
      expect(result.current.error).toBe('Please enter a 6-digit code');
      expect(mockDisableCreate).not.toHaveBeenCalled();
    });

    it('should reject empty code', async () => {
      const { result } = renderHook(() => useTwoFactorStatus());

      let success: boolean;
      await act(async () => {
        success = await result.current.disable2FA('');
      });

      expect(success!).toBe(false);
      expect(result.current.error).toBe('Please enter a 6-digit code');
    });

    it('should handle disable error', async () => {
      mockDisableCreate.mockRejectedValue(new Error('Invalid verification code'));

      const { result } = renderHook(() => useTwoFactorStatus());

      let success: boolean;
      await act(async () => {
        success = await result.current.disable2FA('123456');
      });

      expect(success!).toBe(false);
      expect(result.current.error).toBe('Invalid verification code');
    });
  });

  describe('clearError', () => {
    it('should clear error', async () => {
      mockDevicesRetrieve.mockRejectedValue(new Error('Some error'));

      const { result } = renderHook(() => useTwoFactorStatus());

      await act(async () => {
        await result.current.fetchStatus();
      });

      expect(result.current.error).toBe('Some error');

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });
});
