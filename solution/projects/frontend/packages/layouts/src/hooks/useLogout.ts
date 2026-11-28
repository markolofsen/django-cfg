'use client';

import { useCallback } from 'react';

import { useAuth } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';

/**
 * Hook for logout with i18n confirmation dialog.
 *
 * @example
 * ```tsx
 * function UserMenu() {
 *   const handleLogout = useLogout();
 *   return <Button onClick={handleLogout}>Logout</Button>;
 * }
 * ```
 */
export function useLogout() {
  const { logout } = useAuth();
  const t = useAppT();

  const handleLogout = useCallback(async () => {
    const confirmed = await window.dialog.confirm({
      title: t('api.logout.title'),
      message: t('api.logout.message'),
      confirmText: t('api.logout.confirm'),
      cancelText: t('api.logout.cancel'),
      variant: 'destructive',
    });

    if (confirmed) {
      logout();
    }
  }, [logout, t]);

  return handleLogout;
}
