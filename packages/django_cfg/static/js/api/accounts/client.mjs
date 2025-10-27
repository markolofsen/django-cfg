import { BaseAPIClient } from '../base.mjs';

/**
 * Accounts API Client
 * Auto-generated from OpenAPI schema
 * @module accounts
 * @extends BaseAPIClient
 */
export class AccountsAPI extends BaseAPIClient {
    /**
     * Initialize accounts API client
     * @param {string} [baseURL] - Optional base URL
     */
    constructor(baseURL) {
        super(baseURL);
    }

    /**
     * accountsOtpRequestCreate     * Request OTP code to email or phone.     * @param {OTPRequestRequest} data - Request body     * @returns {Promise<OTPRequestResponse>} Response data
     */
    async accountsOtpRequestCreate(data) {
        const path = `/cfg/accounts/otp/request/`;        return this.post(path, data);    }
    /**
     * accountsOtpVerifyCreate     * Verify OTP code and return JWT tokens.     * @param {OTPVerifyRequest} data - Request body     * @returns {Promise<OTPVerifyResponse>} Response data
     */
    async accountsOtpVerifyCreate(data) {
        const path = `/cfg/accounts/otp/verify/`;        return this.post(path, data);    }
    /**
     * Get current user profile     * Retrieve the current authenticated user's profile information.     * @returns {Promise<User>} Response data
     */
    async accountsProfileRetrieve() {
        const path = `/cfg/accounts/profile/`;        return this.get(path);    }
    /**
     * Upload user avatar     * Upload avatar image for the current authenticated user. Accepts multipart/form-data with 'avatar' field.     * @param {any} data - Request body     * @returns {Promise<User>} Response data
     */
    async accountsProfileAvatarCreate(data) {
        const path = `/cfg/accounts/profile/avatar/`;        return this.post(path, data);    }
    /**
     * Partial update user profile     * Partially update the current authenticated user's profile information. Supports avatar upload.     * @param {UserProfileUpdateRequest} data - Request body     * @returns {Promise<User>} Response data
     */
    async accountsProfilePartialUpdate(data) {
        const path = `/cfg/accounts/profile/partial/`;        return this.put(path, data);    }
    /**
     * Partial update user profile     * Partially update the current authenticated user's profile information. Supports avatar upload.     * @param {PatchedUserProfileUpdateRequest} data - Request body     * @returns {Promise<User>} Response data
     */
    async accountsProfilePartialPartialUpdate(data) {
        const path = `/cfg/accounts/profile/partial/`;        return this.patch(path, data);    }
    /**
     * Update user profile     * Update the current authenticated user's profile information.     * @param {UserProfileUpdateRequest} data - Request body     * @returns {Promise<User>} Response data
     */
    async accountsProfileUpdateUpdate(data) {
        const path = `/cfg/accounts/profile/update/`;        return this.put(path, data);    }
    /**
     * Update user profile     * Update the current authenticated user's profile information.     * @param {PatchedUserProfileUpdateRequest} data - Request body     * @returns {Promise<User>} Response data
     */
    async accountsProfileUpdatePartialUpdate(data) {
        const path = `/cfg/accounts/profile/update/`;        return this.patch(path, data);    }
    /**
     * accountsTokenRefreshCreate     * Refresh JWT token.     * @param {TokenRefreshRequest} data - Request body     * @returns {Promise<TokenRefresh>} Response data
     */
    async accountsTokenRefreshCreate(data) {
        const path = `/cfg/accounts/token/refresh/`;        return this.post(path, data);    }
}

// Default instance for convenience
export const accountsAPI = new AccountsAPI();

// Default export
export default AccountsAPI;