'use client';

import { useCallback, useState } from 'react';

import { cfgTotpDevicesRetrieve, cfgTotpDisableCreate } from '../../_api/endpoints';
import { authLogger } from '../utils/logger';
import { formatAuthError, logAuthFailure } from '../utils/errors';
import { isValidTotpCode } from './twoFactor.shared';

export interface TwoFactorDevice {
  id: string;
  name: string;
  createdAt: string;
  lastUsedAt: string | null;
  isPrimary: boolean;
}

export interface UseTwoFactorStatusReturn {
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
  /** Whether 2FA is enabled for user */
  has2FAEnabled: boolean | null;
  /** List of TOTP devices */
  devices: TwoFactorDevice[];
  /** Fetch 2FA status */
  fetchStatus: () => Promise<void>;
  /** Disable 2FA (requires TOTP code) */
  disable2FA: (code: string) => Promise<boolean>;
  /** Clear error */
  clearError: () => void;
}

/**
 * Read and manage 2FA status (internal, composed by {@link useTwoFactor}).
 *
 * Fetches the device list / enabled flag and disables 2FA.
 */
export const useTwoFactorStatus = (): UseTwoFactorStatusReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [has2FAEnabled, setHas2FAEnabled] = useState<boolean | null>(null);
  const [devices, setDevices] = useState<TwoFactorDevice[]>([]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const fetchStatus = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      authLogger.info('Fetching 2FA status...');

      // API returns { devices: [...], has_2fa_enabled: bool }
      const response = await cfgTotpDevicesRetrieve();

      const mappedDevices: TwoFactorDevice[] = response.devices.map((device) => ({
        id: device.id,
        name: device.name,
        createdAt: device.created_at,
        lastUsedAt: device.last_used_at ?? null,
        isPrimary: device.is_primary,
      }));

      setDevices(mappedDevices);
      setHas2FAEnabled(response.has_2fa_enabled);

      authLogger.info('2FA status:', response.has_2fa_enabled ? 'enabled' : 'disabled');
    } catch (err) {
      const errorMessage = formatAuthError(err, 'Failed to fetch 2FA status');
      logAuthFailure(authLogger, 'Failed to fetch 2FA status:', err);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const disable2FA = useCallback(async (code: string): Promise<boolean> => {
    if (!isValidTotpCode(code)) {
      setError('Please enter a 6-digit code');
      return false;
    }

    setIsLoading(true);
    setError(null);

    try {
      authLogger.info('Disabling 2FA...');

      await cfgTotpDisableCreate({ code });

      setHas2FAEnabled(false);
      setDevices([]);

      authLogger.info('2FA disabled successfully');
      return true;
    } catch (err: unknown) {
      const errorMessage = formatAuthError(err, 'Invalid verification code');
      logAuthFailure(authLogger, 'Failed to disable 2FA:', err);
      setError(errorMessage);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    has2FAEnabled,
    devices,
    fetchStatus,
    disable2FA,
    clearError,
  };
};
