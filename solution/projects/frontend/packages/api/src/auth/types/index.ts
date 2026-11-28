/**
 * Auth Types - Single source of truth
 */

// Form types (auth logic only)
export type {
  AuthStep,
  AuthFormState,
  AuthFormStateHandlers,
  AuthFormSubmitHandlers,
  AuthFormValidation,
  AuthFormAutoSubmit,
  AuthFormReturn,
  UseAuthFormOptions,
  OTPRequestResult,
  OTPRequestConsent,
  PasswordLoginOptions,
  PasswordLoginResult,
  WebmailLink,
} from './form';

// Re-export context types
export type {
  UserProfile,
  AuthConfig,
  AuthContextType,
  AuthProviderProps,
} from '../context/types';
