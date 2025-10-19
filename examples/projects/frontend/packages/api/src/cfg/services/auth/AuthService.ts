/**
 * Authentication Service
 *
 * Handles OTP authentication, token management, and user profile
 */

import { BaseClient } from '../../BaseClient';
import { APIError, CfgAccountsTypes, CfgUserProfileTypes, Enums } from '../../generated';

export class AuthService extends BaseClient {
  /**
   * Request OTP code
   */
  static async requestOTP(
    identifier: string,
    channel?: Enums.OTPRequestRequestChannel
  ): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> {
    try {
      const response = await this.api.cfg_accounts.otpRequestCreate({
        identifier,
        channel,
      });
      return { success: true, message: response.message };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Verify OTP and login
   */
  static async verifyOTP(
    identifier: string,
    otp: string,
    channel?: Enums.OTPVerifyRequestChannel
  ): Promise<{
    success: boolean;
    user?: CfgUserProfileTypes.User;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const { access, refresh } = await this.api.cfg_accounts.otpVerifyCreate({
        identifier,
        otp,
        channel,
      });

      this.api.setToken(access, refresh);

      const user = await this.api.cfg_user_profile.accountsProfileRetrieve();

      return { success: true, user };
    } catch (error) {
      if (error instanceof APIError) {
        if (error.isValidationError && error.fieldErrors) {
          return { success: false, fieldErrors: error.fieldErrors };
        }
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Get current user profile
   */
  static async getCurrentUser(): Promise<{
    success: boolean;
    user?: CfgUserProfileTypes.User;
    error?: string;
  }> {
    try {
      const user = await this.api.cfg_user_profile.accountsProfileRetrieve();
      return { success: true, user };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Update user profile
   */
  static async updateProfile(
    data: CfgUserProfileTypes.PatchedUserProfileUpdateRequest
  ): Promise<{
    success: boolean;
    user?: CfgUserProfileTypes.User;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const user = await this.api.cfg_user_profile.accountsProfilePartialUpdate(data);
      return { success: true, user };
    } catch (error) {
      if (error instanceof APIError) {
        if (error.isValidationError && error.fieldErrors) {
          return { success: false, fieldErrors: error.fieldErrors };
        }
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Refresh access token
   */
  static async refreshToken(): Promise<{ success: boolean; error?: string }> {
    const refresh = this.api.getRefreshToken();
    if (!refresh) {
      return { success: false, error: 'No refresh token' };
    }

    try {
      const { access } = await this.api.cfg_auth.accountsTokenRefreshCreate({ refresh });
      this.api.setToken(access);
      return { success: true };
    } catch (error) {
      this.api.clearTokens();
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Logout user
   */
  static logout(): void {
    this.api.clearTokens();
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    return this.api.isAuthenticated();
  }

  /**
   * Get access token
   */
  static getToken(): string | null {
    return this.api.getToken();
  }

  /**
   * Get refresh token
   */
  static getRefreshToken(): string | null {
    return this.api.getRefreshToken();
  }
}
