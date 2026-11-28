import { CFG_KEYS } from '../../runtime/keys';
import { useCfgStored } from './useCfgStored';

const AUTH_REDIRECT_KEY = CFG_KEYS.redirectUrl.key;

export interface AuthRedirectOptions {
  fallbackUrl?: string;
  clearOnUse?: boolean;
}

/**
 * Read redirect URL directly from sessionStorage (bypasses React state)
 * This is needed because different component instances have different React states
 */
const getRedirectFromStorage = (): string => {
  if (typeof window === 'undefined') return '';
  try {
    const item = window.sessionStorage.getItem(AUTH_REDIRECT_KEY);
    return item ? JSON.parse(item) : '';
  } catch {
    return '';
  }
};

/**
 * Clear redirect URL directly from sessionStorage
 */
const clearRedirectFromStorage = (): void => {
  if (typeof window === 'undefined') return;
  try {
    window.sessionStorage.removeItem(AUTH_REDIRECT_KEY);
    window.sessionStorage.removeItem(`${AUTH_REDIRECT_KEY}_ts`);
  } catch {
    // Ignore errors
  }
};

/**
 * Read the saved back-url without clearing it. Null when nothing saved —
 * unlike getFinalRedirectUrl, never substitutes a fallback.
 */
export const peekSavedRedirect = (): string | null => getRedirectFromStorage() || null;

/**
 * Read AND clear the saved back-url (single-use intent). Null when nothing
 * saved. This is the one primitive every post-auth navigator uses to honor
 * "return the user to where the guard bounced them from".
 */
export const consumeSavedRedirect = (): string | null => {
  const stored = getRedirectFromStorage();
  if (stored) clearRedirectFromStorage();
  return stored || null;
};

export const useAuthRedirectManager = (options: AuthRedirectOptions = {}) => {
  const { fallbackUrl = '/private', clearOnUse = true } = options;
  const [storedRedirect, setRedirectUrl, removeRedirectUrl] = useCfgStored(CFG_KEYS.redirectUrl, { json: true });
  const redirectUrl = storedRedirect ?? '';

  const setRedirect = (url: string) => {
    setRedirectUrl(url);
  };

  const getRedirect = () => {
    // Read directly from storage to get latest value across components
    return getRedirectFromStorage() || redirectUrl;
  };

  const clearRedirect = () => {
    removeRedirectUrl();
    clearRedirectFromStorage();
  };

  const hasRedirect = () => {
    const stored = getRedirectFromStorage();
    return stored.length > 0 || redirectUrl.length > 0;
  };

  const getFinalRedirectUrl = () => {
    // Read directly from storage to get latest value across components
    const stored = getRedirectFromStorage();
    return stored || redirectUrl || fallbackUrl;
  };

  const useAndClearRedirect = () => {
    // Read directly from storage to ensure we get the latest saved URL
    // even if it was saved by a different component instance
    const stored = getRedirectFromStorage();
    const finalUrl = stored || redirectUrl || fallbackUrl;

    if (clearOnUse) {
      clearRedirect();
    }
    return finalUrl;
  };

  return {
    redirectUrl,
    setRedirect,
    getRedirect,
    clearRedirect,
    hasRedirect,
    getFinalRedirectUrl,
    useAndClearRedirect
  };
}; 
