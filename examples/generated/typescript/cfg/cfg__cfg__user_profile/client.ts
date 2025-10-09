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
  async cfgAccountsProfileRetrieve(): Promise<Models.User> {
    const response = await this.client.request('GET', "/cfg/accounts/profile/");
    return response;
  }

  /**
   * Upload user avatar
   * 
   * Upload avatar image for the current authenticated user. Accepts
   * multipart/form-data with 'avatar' field.
   */
  async cfgAccountsProfileAvatarCreate(data: FormData): Promise<Models.User> {
    const response = await this.client.request('POST', "/cfg/accounts/profile/avatar/", { body: data });
    return response;
  }

  /**
   * Partial update user profile
   * 
   * Partially update the current authenticated user's profile information.
   * Supports avatar upload.
   */
  async cfgAccountsProfilePartialUpdate(data: Models.UserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PUT', "/cfg/accounts/profile/partial/", { body: data });
    return response;
  }

  /**
   * Partial update user profile
   * 
   * Partially update the current authenticated user's profile information.
   * Supports avatar upload.
   */
  async cfgAccountsProfilePartialPartialUpdate(data?: Models.PatchedUserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PATCH', "/cfg/accounts/profile/partial/", { body: data });
    return response;
  }

  /**
   * Update user profile
   * 
   * Update the current authenticated user's profile information.
   */
  async cfgAccountsProfileUpdateUpdate(data: Models.UserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PUT', "/cfg/accounts/profile/update/", { body: data });
    return response;
  }

  /**
   * Update user profile
   * 
   * Update the current authenticated user's profile information.
   */
  async cfgAccountsProfileUpdatePartialUpdate(data?: Models.PatchedUserProfileUpdateRequest): Promise<Models.User> {
    const response = await this.client.request('PATCH', "/cfg/accounts/profile/update/", { body: data });
    return response;
  }

}