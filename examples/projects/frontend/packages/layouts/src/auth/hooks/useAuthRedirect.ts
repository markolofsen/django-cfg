import { useSessionStorage } from './useSessionStorage';

const AUTH_REDIRECT_KEY = 'auth_redirect_url';

export interface AuthRedirectOptions {
  fallbackUrl?: string;
  clearOnUse?: boolean;
}

export const useAuthRedirectManager = (options: AuthRedirectOptions = {}) => {
  const { fallbackUrl = '/dashboard', clearOnUse = true } = options;
  const [redirectUrl, setRedirectUrl, removeRedirectUrl] = useSessionStorage<string>(AUTH_REDIRECT_KEY, '');

  const setRedirect = (url: string) => {
    setRedirectUrl(url);
  };

  const getRedirect = () => {
    return redirectUrl;
  };

  const clearRedirect = () => {
    removeRedirectUrl();
  };

  const hasRedirect = () => {
    return redirectUrl.length > 0;
  };

  const getFinalRedirectUrl = () => {
    return redirectUrl || fallbackUrl;
  };

  const useAndClearRedirect = () => {
    const finalUrl = getFinalRedirectUrl();
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