/**
 * Email validation utility
 */
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * OTP validation utility
 */
export const validateOTP = (otp: string): boolean => {
  return /^\d{6}$/.test(otp);
}; 