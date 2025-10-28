import * as Models from "./models";


/**
 * API endpoints for User Profile.
 */
export class CfgUserProfile {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get current user profile
   * 
   * Retrieve the current authenticated user's profile information.
   */
  async accountsProfileRetrieve(): Promise<Models.User> {
    const response = await this.client.request('GET', "/cfg/accounts/profile/");
    return response;
  }

  /**
   * Upload user avatar
   * 
   * Upload avatar image for the current authenticated user. Accepts
   * multipart/form-data with 'avatar' field.
   */
  async accountsProfileAvatarCreate(data: FormData): Promise<Models.User> {
    const response = await this.client.request('POST', "/cfg/accounts/profile/avatar/", { formData: data });
    return response;
  }

  /**
   * Partial update user profile
   * 
   * Partially update the current authenticated user's profile information.
   * Supports avatar upload.
   */
  async accountsProfilePartialUpdate(data: Models.UserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PUT', "/cfg/accounts/profile/partial/", { body: data });
    return response;
  }

  /**
   * Partial update user profile
   * 
   * Partially update the current authenticated user's profile information.
   * Supports avatar upload.
   */
  async accountsProfilePartialPartialUpdate(data?: Models.PatchedUserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PATCH', "/cfg/accounts/profile/partial/", { body: data });
    return response;
  }

  /**
   * Update user profile
   * 
   * Update the current authenticated user's profile information.
   */
  async accountsProfileUpdateUpdate(data: Models.UserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PUT', "/cfg/accounts/profile/update/", { body: data });
    return response;
  }

  /**
   * Update user profile
   * 
   * Update the current authenticated user's profile information.
   */
  async accountsProfileUpdatePartialUpdate(data?: Models.PatchedUserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PATCH', "/cfg/accounts/profile/update/", { body: data });
    return response;
  }

}