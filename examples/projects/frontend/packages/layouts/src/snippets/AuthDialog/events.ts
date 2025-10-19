export const AUTH_EVENTS = {
  OPEN_AUTH_DIALOG: 'OPEN_AUTH_DIALOG',
  CLOSE_AUTH_DIALOG: 'CLOSE_AUTH_DIALOG',
  AUTH_SUCCESS: 'AUTH_SUCCESS',
  AUTH_FAILURE: 'AUTH_FAILURE',
} as const;

export type AuthEventType = typeof AUTH_EVENTS[keyof typeof AUTH_EVENTS];

export interface OpenAuthDialogPayload {
  message?: string;
  redirectUrl?: string;
}

export interface AuthSuccessPayload {
  user?: any;
}

export interface AuthFailurePayload {
  error?: string;
}
