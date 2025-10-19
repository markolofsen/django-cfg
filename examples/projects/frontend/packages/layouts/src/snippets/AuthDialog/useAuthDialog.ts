import { useCallback } from 'react';

import { AUTH_EVENTS, type OpenAuthDialogPayload } from './events';
import { events } from '@djangocfg/ui';

/**
 * Hook to control auth dialog from anywhere in the app
 */
export function useAuthDialog() {
  const openAuthDialog = useCallback((options?: OpenAuthDialogPayload) => {
    events.publish({
      type: AUTH_EVENTS.OPEN_AUTH_DIALOG,
      payload: options,
    });
  }, []);

  const closeAuthDialog = useCallback(() => {
    events.publish({
      type: AUTH_EVENTS.CLOSE_AUTH_DIALOG,
    });
  }, []);

  return {
    openAuthDialog,
    closeAuthDialog,
  };
}
