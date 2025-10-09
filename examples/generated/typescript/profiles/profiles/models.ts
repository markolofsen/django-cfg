/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedUserProfileList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<UserProfile>;
}

/**
 * Serializer for user profiles.
 * 
 * Request model (no read-only fields).
 */
export interface UserProfileRequest {
  website?: string;
  github?: string;
  twitter?: string;
  linkedin?: string;
  company?: string;
  job_title?: string;
}

/**
 * Serializer for user profiles.
 * 
 * Response model (includes read-only fields).
 */
export interface UserProfile {
  id: number;
  user: number;
  /** Get basic user information. */
  user_info: Record<string, any>;
  website?: string;
  github?: string;
  twitter?: string;
  linkedin?: string;
  company?: string;
  job_title?: string;
  posts_count: number;
  comments_count: number;
  orders_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * Serializer for updating user profiles.
 * 
 * Request model (no read-only fields).
 */
export interface UserProfileUpdateRequest {
  website?: string;
  github?: string;
  twitter?: string;
  linkedin?: string;
  company?: string;
  job_title?: string;
}

/**
 * Serializer for updating user profiles.
 * 
 * Response model (includes read-only fields).
 */
export interface UserProfileUpdate {
  website?: string;
  github?: string;
  twitter?: string;
  linkedin?: string;
  company?: string;
  job_title?: string;
}

/**
 * Serializer for updating user profiles.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedUserProfileUpdateRequest {
  website?: string;
  github?: string;
  twitter?: string;
  linkedin?: string;
  company?: string;
  job_title?: string;
}

/**
 * Serializer for user profiles.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedUserProfileRequest {
  website?: string;
  github?: string;
  twitter?: string;
  linkedin?: string;
  company?: string;
  job_title?: string;
}

/**
 * Serializer for profile statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface UserProfileStats {
  total_profiles: number;
  profiles_with_company: number;
  profiles_with_social_links: number;
  most_active_users: Array<UserProfile>;
}

