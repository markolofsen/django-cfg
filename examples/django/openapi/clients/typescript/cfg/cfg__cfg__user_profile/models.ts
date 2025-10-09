/**
 * Serializer for user details.
 * 
 * Response model (includes read-only fields).
 */
export interface User {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  /** Get user's full name. */
  full_name: string;
  /** Get user's initials for avatar fallback. */
  initials: string;
  /** Get formatted username for display. */
  display_username: string;
  company?: string;
  phone?: string;
  position?: string;
  avatar?: string;
  /** Designates whether the user can log into this admin site. */
  is_staff: boolean;
  /** Designates that this user has all permissions without explicitly assigning them. */
  is_superuser: boolean;
  date_joined: string;
  last_login?: string;
  /** Get count of unanswered messages for the user. */
  unanswered_messages_count: number;
}

/**
 * Serializer for updating user profile.
 * 
 * Request model (no read-only fields).
 */
export interface UserProfileUpdateRequest {
  first_name?: string;
  last_name?: string;
  company?: string;
  phone?: string;
  position?: string;
}

/**
 * Serializer for updating user profile.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedUserProfileUpdateRequest {
  first_name?: string;
  last_name?: string;
  company?: string;
  phone?: string;
  position?: string;
}

