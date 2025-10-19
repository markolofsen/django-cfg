/**
 * Format authentication error messages
 */
export const formatAuthError = (error: any): string => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error?.message) {
    return error.message;
  }
  
  if (error?.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error?.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  return 'An unexpected error occurred';
};

/**
 * Common error messages
 */
export const AUTH_ERRORS = {
  INVALID_EMAIL: 'Please enter a valid email address',
  INVALID_OTP: 'Please enter a valid 6-digit verification code',
  NETWORK_ERROR: 'Network error. Please check your connection',
  SERVER_ERROR: 'Server error. Please try again later',
  UNAUTHORIZED: 'Unauthorized. Please sign in again',
  TOKEN_EXPIRED: 'Session expired. Please sign in again',
} as const; 