import * as Models from "./models";


/**
 * API endpoints for Profiles.
 */
export class ProfilesProfiles {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async profilesList(ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedUserProfileList>;
  async profilesList(params?: { ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedUserProfileList>;

  /**
   * List user profiles
   * 
   * Get a paginated list of all user profiles
   */
  async profilesList(...args: any[]): Promise<Models.PaginatedUserProfileList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3] };
    }
    const response = await this.client.request('GET', "/api/profiles/profiles/", { params });
    return response;
  }

  /**
   * Create user profile
   * 
   * Create a new user profile
   */
  async profilesCreate(data: Models.UserProfileRequest): Promise<Models.UserProfile> {
    const response = await this.client.request('POST', "/api/profiles/profiles/", { body: data });
    return response;
  }

  /**
   * Get user profile
   * 
   * Get detailed information about a specific user profile
   */
  async profilesRetrieve(id: number): Promise<Models.UserProfile> {
    const response = await this.client.request('GET', `/api/profiles/profiles/${id}/`);
    return response;
  }

  /**
   * Update user profile
   * 
   * Update user profile information
   */
  async profilesUpdate(id: number, data: Models.UserProfileUpdateRequest): Promise<Models.UserProfileUpdate> {
    const response = await this.client.request('PUT', `/api/profiles/profiles/${id}/`, { body: data });
    return response;
  }

  /**
   * Partially update user profile
   * 
   * Partially update user profile information
   */
  async profilesPartialUpdate(id: number, data?: Models.PatchedUserProfileUpdateRequest): Promise<Models.UserProfileUpdate> {
    const response = await this.client.request('PATCH', `/api/profiles/profiles/${id}/`, { body: data });
    return response;
  }

  /**
   * Delete user profile
   * 
   * Delete a user profile
   */
  async profilesDestroy(id: number): Promise<void> {
    const response = await this.client.request('DELETE', `/api/profiles/profiles/${id}/`);
    return;
  }

  /**
   * Get my profile
   * 
   * Get current user's profile
   */
  async profilesMeRetrieve(): Promise<Models.UserProfile> {
    const response = await this.client.request('GET', "/api/profiles/profiles/me/");
    return response;
  }

  /**
   * Get my profile
   * 
   * Get current user's profile
   */
  async profilesMeUpdate(data: Models.UserProfileRequest): Promise<Models.UserProfile> {
    const response = await this.client.request('PUT', "/api/profiles/profiles/me/", { body: data });
    return response;
  }

  /**
   * Get my profile
   * 
   * Get current user's profile
   */
  async profilesMePartialUpdate(data?: Models.PatchedUserProfileRequest): Promise<Models.UserProfile> {
    const response = await this.client.request('PATCH', "/api/profiles/profiles/me/", { body: data });
    return response;
  }

  /**
   * Get profile statistics
   * 
   * Get comprehensive profile statistics
   */
  async profilesStatsRetrieve(): Promise<Models.UserProfileStats> {
    const response = await this.client.request('GET', "/api/profiles/profiles/stats/");
    return response;
  }

}