'use client';

import { useCallback, useState } from 'react';

import { cfgAccountsProfileDeleteCreate } from '../../_api/endpoints';
import { useAuth } from '../context';
import { authLogger } from '../utils/logger';

export interface DeleteAccountResult {
  success: boolean;
  message: string;
}

export interface UseDeleteAccountReturn {
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
  /** Delete the account */
  deleteAccount: () => Promise<DeleteAccountResult>;
  /** Clear error */
  clearError: () => void;
}

/**
 * Hook for deleting user account.
 *
 * This performs a soft delete - deactivates the account and anonymizes personal data.
 * The account can be restored by an administrator if needed.
 *
 * @example
 * ```tsx
 * const { deleteAccount, isLoading, error } = useDeleteAccount();
 *
 * const handleDelete = async () => {
 *   await deleteAccount(); // Signs out after a successful deletion.
 * };
 * ```
 */
export const useDeleteAccount = (): UseDeleteAccountReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { logout } = useAuth();

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Delete the user account (soft delete)
   */
  const deleteAccount = useCallback(async (): Promise<DeleteAccountResult> => {
    setIsLoading(true);
    setError(null);

    try {
      authLogger.info('Deleting account...');

      const response = await cfgAccountsProfileDeleteCreate();

      if (!response.success) {
        authLogger.error('Failed to delete account:', response.message);
        setError(response.message);
        throw new Error(response.message);
      }
    } catch (error) {
      authLogger.error('Failed to delete account:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }

    await logout();
    return { success: true, message: 'Account deleted successfully' };
  }, [logout]);

  return {
    isLoading,
    error,
    deleteAccount,
    clearError,
  };
};
