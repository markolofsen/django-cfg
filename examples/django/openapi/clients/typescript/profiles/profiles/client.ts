import * as Models from "./models";


/**
 * API endpoints for Profiles.
 */
export class ProfilesProfilesAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List user profiles
 * 
 * Get a paginated list of all user profiles
 */
async profilesList(page?: number | null, page_size?: number | null): Promise<Models.PaginatedUserProfileList[]> {
  const response = await this.client.request<Models.PaginatedUserProfileList[]>('GET', "/profiles/profiles/", { params: { page, page_size } });
  return (response as any).results || [];
}

  /**
 * Create user profile
 * 
 * Create a new user profile
 */
async profilesCreate(data: Models.UserProfileRequest): Promise<Models.UserProfile> {
  const response = await this.client.request<Models.UserProfile>('POST', "/profiles/profiles/", { body: data });
  return response;
}

  /**
 * Get user profile
 * 
 * Get detailed information about a specific user profile
 */
async profilesRetrieve(id: number): Promise<Models.UserProfile> {
  const response = await this.client.request<Models.UserProfile>('GET', `/profiles/profiles/${id}/`);
  return response;
}

  /**
 * Update user profile
 * 
 * Update user profile information
 */
async profilesUpdate(id: number, data: Models.UserProfileUpdateRequest): Promise<Models.UserProfileUpdate> {
  const response = await this.client.request<Models.UserProfileUpdate>('PUT', `/profiles/profiles/${id}/`, { body: data });
  return response;
}

  /**
 * Partially update user profile
 * 
 * Partially update user profile information
 */
async profilesPartialUpdate(id: number, data?: Models.PatchedUserProfileUpdateRequest): Promise<Models.UserProfileUpdate> {
  const response = await this.client.request<Models.UserProfileUpdate>('PATCH', `/profiles/profiles/${id}/`, { body: data });
  return response;
}

  /**
 * Delete user profile
 * 
 * Delete a user profile
 */
async profilesDestroy(id: number): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/profiles/profiles/${id}/`);
  return;
}

  /**
 * Get my profile
 * 
 * Get current user's profile
 */
async profilesMeRetrieve(): Promise<Models.UserProfile> {
  const response = await this.client.request<Models.UserProfile>('GET', "/profiles/profiles/me/");
  return response;
}

  /**
 * Get my profile
 * 
 * Get current user's profile
 */
async profilesMeUpdate(data: Models.UserProfileRequest): Promise<Models.UserProfile> {
  const response = await this.client.request<Models.UserProfile>('PUT', "/profiles/profiles/me/", { body: data });
  return response;
}

  /**
 * Get my profile
 * 
 * Get current user's profile
 */
async profilesMePartialUpdate(data?: Models.PatchedUserProfileRequest): Promise<Models.UserProfile> {
  const response = await this.client.request<Models.UserProfile>('PATCH', "/profiles/profiles/me/", { body: data });
  return response;
}

  /**
 * Get profile statistics
 * 
 * Get comprehensive profile statistics
 */
async profilesStatsRetrieve(): Promise<Models.UserProfileStats> {
  const response = await this.client.request<Models.UserProfileStats>('GET', "/profiles/profiles/stats/");
  return response;
}

}