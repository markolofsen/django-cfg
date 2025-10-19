import { useCallback, useEffect, useState } from 'react';

import { useAuth } from '../context';
import { useAutoAuth } from './useAutoAuth';
import { useLocalStorage } from './useLocalStorage';

export interface AuthFormState {
  identifier: string; // Email or phone number
  channel: 'email' | 'phone';
  otp: string;
  isLoading: boolean;
  acceptedTerms: boolean;
  step: 'identifier' | 'otp';
  error: string;
}

export interface AuthFormHandlers {
  setIdentifier: (identifier: string) => void;
  setChannel: (channel: 'email' | 'phone') => void;
  setOtp: (otp: string) => void;
  setAcceptedTerms: (accepted: boolean) => void;
  setError: (error: string) => void;
  clearError: () => void;
  handleIdentifierSubmit: (e: React.FormEvent) => Promise<void>;
  handleOTPSubmit: (e: React.FormEvent) => Promise<void>;
  handleResendOTP: () => Promise<void>;
  handleBackToIdentifier: () => void;
  forceOTPStep: () => void;
  // Utility methods
  detectChannelFromIdentifier: (identifier: string) => 'email' | 'phone' | null;
  validateIdentifier: (identifier: string, channel?: 'email' | 'phone') => boolean;
}

export interface UseAuthFormOptions {
  onIdentifierSuccess?: (identifier: string, channel: 'email' | 'phone') => void;
  onOTPSuccess?: () => void;
  onError?: (message: string) => void;
  sourceUrl: string;
}

export const useAuthForm = (options: UseAuthFormOptions): AuthFormState & AuthFormHandlers => {
  const { onIdentifierSuccess, onOTPSuccess, onError, sourceUrl } = options;
  
  // Form state
  const [identifier, setIdentifier] = useState('');
  const [channel, setChannel] = useState<'email' | 'phone'>('email');
  const [otp, setOtp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [step, setStep] = useState<'identifier' | 'otp'>('identifier');
  const [error, setError] = useState('');
  

  
  // Auth hooks
  const { requestOTP, verifyOTP, getSavedEmail, saveEmail, getSavedPhone, savePhone } = useAuth();
  const [savedTermsAccepted, setSavedTermsAccepted] = useLocalStorage('auth_terms_accepted', false);
  const [savedEmail, setSavedEmail] = useLocalStorage('auth_email', '');
  const [savedPhone, setSavedPhone] = useLocalStorage('auth_phone', '');

  // Utility functions
  const detectChannelFromIdentifier = useCallback((identifier: string): 'email' | 'phone' | null => {
    if (!identifier) return null;
    
    // Email detection
    if (identifier.includes('@')) {
      return 'email';
    }
    
    // Phone detection (starts with + and contains digits)
    if (identifier.startsWith('+') && /^\+[1-9]\d{6,14}$/.test(identifier)) {
      return 'phone';
    }
    
    return null;
  }, []);

  const validateIdentifier = useCallback((identifier: string, channelType?: 'email' | 'phone'): boolean => {
    if (!identifier) return false;
    
    const detectedChannel = channelType || detectChannelFromIdentifier(identifier);
    
    if (detectedChannel === 'email') {
      // Basic email validation
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(identifier);
    } else if (detectedChannel === 'phone') {
      // E.164 phone validation
      return /^\+[1-9]\d{6,14}$/.test(identifier);
    }
    
    return false;
  }, [detectChannelFromIdentifier]);

  // Load saved data on mount
  useEffect(() => {
    const authSavedEmail = getSavedEmail();
    const authSavedPhone = getSavedPhone();
    
    // Prioritize phone over email if both exist
    if (authSavedPhone) {
      setIdentifier(authSavedPhone);
      setChannel('phone');
    } else if (authSavedEmail) {
      setIdentifier(authSavedEmail);
      setChannel('email');
    }
    
    if (savedTermsAccepted) {
      setAcceptedTerms(savedTermsAccepted);
    }
  }, [getSavedEmail, getSavedPhone, savedTermsAccepted]);

  // Auto-detect channel when identifier changes
  useEffect(() => {
    if (identifier) {
      const detectedChannel = detectChannelFromIdentifier(identifier);
      if (detectedChannel && detectedChannel !== channel) {
        setChannel(detectedChannel);
      }
    }
  }, [identifier, channel, detectChannelFromIdentifier]);



  const clearError = useCallback(() => setError(''), []);

  const handleIdentifierSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!identifier) {
      const message = channel === 'phone' ? 'Please enter your phone number' : 'Please enter your email address';
      setError(message);
      onError?.(message);
      return;
    }

    // Validate identifier format
    if (!validateIdentifier(identifier, channel)) {
      const message = channel === 'phone' 
        ? 'Please enter a valid phone number (e.g., +1234567890)' 
        : 'Please enter a valid email address';
      setError(message);
      onError?.(message);
      return;
    }

    if (!acceptedTerms) {
      const message = 'Please accept the Terms of Service and Privacy Policy';
      setError(message);
      onError?.(message);
      return;
    }

    setIsLoading(true);
    clearError();
    
    try {
      const result = await requestOTP(identifier, channel, sourceUrl);
      
      if (result.success) {
        // Save identifier and terms acceptance on successful request, clear opposite channel
        if (channel === 'email') {
          saveEmail(identifier);
          setSavedPhone(''); // Clear phone storage
        } else if (channel === 'phone') {
          savePhone(identifier);
          setSavedEmail(''); // Clear email storage
        }
        setSavedTermsAccepted(true);
        setStep('otp');
        onIdentifierSuccess?.(identifier, channel);
      } else {
        setError(result.message);
        onError?.(result.message);
      }
    } catch (error) {
      const message = 'An unexpected error occurred';
      setError(message);
      onError?.(message);
    } finally {
      setIsLoading(false);
    }
  }, [identifier, channel, acceptedTerms, validateIdentifier, requestOTP, saveEmail, clearError, setSavedTermsAccepted, onIdentifierSuccess, onError, sourceUrl]);

  const handleOTPSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!otp || otp.length < 6) {
      const message = 'Please enter the 6-digit verification code';
      setError(message);
      onError?.(message);
      return;
    }

    setIsLoading(true);
    clearError();
    
    try {
      const result = await verifyOTP(identifier, otp, channel, sourceUrl);
      
      if (result.success) {
        // Save identifier on successful login, clear opposite channel
        if (channel === 'email') {
          setSavedEmail(identifier);
          setSavedPhone(''); // Clear phone storage
        } else if (channel === 'phone') {
          setSavedPhone(identifier);
          setSavedEmail(''); // Clear email storage
        }
        onOTPSuccess?.();
      } else {
        setError(result.message);
        onError?.(result.message);
      }
    } catch (error) {
      const message = 'An unexpected error occurred';
      setError(message);
      onError?.(message);
    } finally {
      setIsLoading(false);
    }
  }, [identifier, otp, channel, verifyOTP, clearError, setSavedEmail, onOTPSuccess, onError, sourceUrl]);

  const handleResendOTP = useCallback(async () => {
    setIsLoading(true);
    clearError();
    
    try {
      const result = await requestOTP(identifier, channel, sourceUrl);
      
      if (result.success) {
        // Save identifier and clear OTP input, clear opposite channel
        if (channel === 'email') {
          saveEmail(identifier);
          setSavedPhone(''); // Clear phone storage
        } else if (channel === 'phone') {
          savePhone(identifier);
          setSavedEmail(''); // Clear email storage
        }
        setOtp('');
      } else {
        setError(result.message);
        onError?.(result.message);
      }
    } catch (error) {
      const message = 'Failed to resend verification code';
      setError(message);
      onError?.(message);
    } finally {
      setIsLoading(false);
    }
  }, [identifier, channel, requestOTP, saveEmail, clearError, setOtp, onError, sourceUrl]);

  const handleBackToIdentifier = useCallback(() => {
    setStep('identifier');
    clearError();
  }, [clearError]);

  const forceOTPStep = useCallback(() => {
    setStep('otp');
    clearError();
  }, [clearError]);

  const handleAcceptedTermsChange = useCallback((checked: boolean) => {
    setAcceptedTerms(checked);
    setSavedTermsAccepted(checked);
  }, [setSavedTermsAccepted]);

  // Auto-detect OTP from URL query parameters
  useAutoAuth({
    onOTPDetected: (otp: string) => {
      console.log('[useAuthForm] OTP detected, auto-submitting');
      
      // Get saved identifier from auth context
      const savedEmail = getSavedEmail();
      const savedPhone = getSavedPhone();
      
      // Prioritize phone over email if both exist
      if (savedPhone) {
        setIdentifier(savedPhone);
        setChannel('phone');
      } else if (savedEmail) {
        setIdentifier(savedEmail);
        setChannel('email');
      }
      
      // Set OTP and force OTP step
      setOtp(otp);
      setStep('otp');
      
      // Auto-submit after a short delay to ensure state is updated
      setTimeout(() => {
        const fakeEvent = { preventDefault: () => {} } as React.FormEvent;
        handleOTPSubmit(fakeEvent);
      }, 200);
    },
    cleanupUrl: true,
  });

  return {
    // Form state
    identifier,
    channel,
    otp,
    isLoading,
    acceptedTerms,
    step,
    error,
    
    // Form handlers
    setIdentifier,
    setChannel,
    setOtp,
    setAcceptedTerms: handleAcceptedTermsChange,
    setError,
    clearError,
    
    // Auth handlers
    handleIdentifierSubmit,
    handleOTPSubmit,
    handleResendOTP,
    handleBackToIdentifier,
    forceOTPStep,
    
    // Utility methods
    detectChannelFromIdentifier,
    validateIdentifier,
  };
}; 