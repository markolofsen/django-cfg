'use client';

import { useCallback, useState } from 'react';

import { cfgTotpSetupConfirmCreate, cfgTotpSetupCreate } from '../../_api/endpoints';
import { authLogger } from '../utils/logger';
import { formatAuthError, logAuthFailure } from '../utils/errors';
import { isValidTotpCode } from './twoFactor.shared';

export interface TwoFactorSetupData {
  /** Device ID to use for confirmation */
  deviceId: string;
  /** Base32-encoded TOTP secret (for manual entry) */
  secret: string;
  /** otpauth:// URI for QR code generation */
  provisioningUri: string;
  /** Base64-encoded QR code image (data URI) */
  qrCodeBase64: string;
  /** Seconds until setup expires */
  expiresIn: number;
}

export interface UseTwoFactorSetupOptions {
  /** Callback when setup is confirmed and backup codes are generated */
  onComplete?: (backupCodes: string[]) => void;
  /** Callback on error */
  onError?: (error: string) => void;
}

export interface UseTwoFactorSetupReturn {
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
  /** Setup data (QR code, secret, etc.) */
  setupData: TwoFactorSetupData | null;
  /** Backup codes after confirmation */
  backupCodes: string[] | null;
  /** Warning message about backup codes */
  backupCodesWarning: string | null;
  /** Current setup step */
  setupStep: 'idle' | 'scanning' | 'confirming' | 'complete';
  /** Start 2FA setup - returns QR code data */
  startSetup: (deviceName?: string) => Promise<TwoFactorSetupData | null>;
  /** Confirm setup with TOTP code - returns backup codes */
  confirmSetup: (code: string) => Promise<string[] | null>;
  /** Reset setup state */
  resetSetup: () => void;
  /** Clear error */
  clearError: () => void;
}

/**
 * 2FA setup — enabling TOTP (internal, composed by {@link useTwoFactor}).
 *
 * Flow: startSetup() → user scans QR → confirmSetup(code) → show backup codes.
 */
export const useTwoFactorSetup = (
  options: UseTwoFactorSetupOptions = {},
): UseTwoFactorSetupReturn => {
  const { onComplete, onError } = options;

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [setupData, setSetupData] = useState<TwoFactorSetupData | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[] | null>(null);
  const [backupCodesWarning, setBackupCodesWarning] = useState<string | null>(null);
  const [setupStep, setSetupStep] = useState<'idle' | 'scanning' | 'confirming' | 'complete'>('idle');

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const resetSetup = useCallback(() => {
    setSetupData(null);
    setBackupCodes(null);
    setBackupCodesWarning(null);
    setSetupStep('idle');
    setError(null);
  }, []);

  const startSetup = useCallback(async (deviceName?: string): Promise<TwoFactorSetupData | null> => {
    setIsLoading(true);
    setError(null);
    setSetupStep('scanning');

    try {
      authLogger.info('Starting 2FA setup...');

      const response = await cfgTotpSetupCreate({ device_name: deviceName });

      const data: TwoFactorSetupData = {
        deviceId: response.device_id,
        secret: response.secret,
        provisioningUri: response.provisioning_uri,
        qrCodeBase64: response.qr_code_base64,
        expiresIn: response.expires_in,
      };

      setSetupData(data);
      authLogger.info('2FA setup initiated, expires in:', data.expiresIn, 'seconds');

      return data;
    } catch (err) {
      const errorMessage = formatAuthError(err, 'Failed to start 2FA setup');
      logAuthFailure(authLogger, '2FA setup failed:', err);
      setError(errorMessage);
      setSetupStep('idle');
      onError?.(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [onError]);

  const confirmSetup = useCallback(async (code: string): Promise<string[] | null> => {
    if (!setupData) {
      const msg = 'Setup not started. Call startSetup() first.';
      setError(msg);
      onError?.(msg);
      return null;
    }
    if (!isValidTotpCode(code)) {
      const msg = 'Please enter a 6-digit code';
      setError(msg);
      onError?.(msg);
      return null;
    }

    setIsLoading(true);
    setError(null);
    setSetupStep('confirming');

    try {
      authLogger.info('Confirming 2FA setup...');

      const response = await cfgTotpSetupConfirmCreate({ device_id: setupData.deviceId, code });

      const codes = response.backup_codes;
      setBackupCodes(codes);
      setBackupCodesWarning(response.backup_codes_warning);
      setSetupStep('complete');

      authLogger.info('2FA setup confirmed, backup codes generated:', codes.length);

      onComplete?.(codes);
      return codes;
    } catch (err) {
      const errorMessage = formatAuthError(err, 'Invalid code. Please try again.');
      logAuthFailure(authLogger, '2FA setup confirmation failed:', err);
      setError(errorMessage);
      setSetupStep('scanning'); // Go back to scanning step
      onError?.(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [setupData, onComplete, onError]);

  return {
    isLoading,
    error,
    setupData,
    backupCodes,
    backupCodesWarning,
    setupStep,
    startSetup,
    confirmSetup,
    resetSetup,
    clearError,
  };
};
