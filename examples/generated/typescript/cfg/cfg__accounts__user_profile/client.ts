import * as Models from "./models";


/**
 * API endpoints for User Profile.
 */
export class CfgUserProfileAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get current user profile
   * 
   * Retrieve the current authenticated user's profile information.
   */
  async profileRetrieve(): Promise<Models.User> {
    const response = await this.client.request('GET', "/django_cfg_accounts/profile/");
    return response;
  }

  /**
   * Upload user avatar
   * 
   * Upload avatar image for the current authenticated user. Accepts
   * multipart/form-data with 'avatar' field.
   */
  async profileAvatarCreate(data: FormData): Promise<Models.User> {
    const response = await this.client.request('POST', "/django_cfg_accounts/profile/avatar/", { body: data });
    return response;
  }

  /**
   * Partial update user profile
   * 
   * Partially update the current authenticated user's profile information.
   * Supports avatar upload.
   */
  async profilePartialUpdate(data: Models.UserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PUT', "/django_cfg_accounts/profile/partial/", { body: data });
    return response;
  }

  /**
   * Partial update user profile
   * 
   * Partially update the current authenticated user's profile information.
   * Supports avatar upload.
   */
  async profilePartialPartialUpdate(data?: Models.PatchedUserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PATCH', "/django_cfg_accounts/profile/partial/", { body: data });
    return response;
  }

  /**
   * Update user profile
   * 
   * Update the current authenticated user's profile information.
   */
  async profileUpdateUpdate(data: Models.UserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PUT', "/django_cfg_accounts/profile/update/", { body: data });
    return response;
  }

  /**
   * Update user profile
   * 
   * Update the current authenticated user's profile information.
   */
  async profileUpdatePartialUpdate(data?: Models.PatchedUserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PATCH', "/django_cfg_accounts/profile/update/", { body: data });
    return response;
  }

}