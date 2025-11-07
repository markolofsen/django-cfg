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
  avatar?: string | null;
  /** Designates whether the user can log into this admin site. */
  is_staff: boolean;
  /** Designates that this user has all permissions without explicitly assigning them. */
  is_superuser: boolean;
  date_joined: string;
  last_login?: string | null;
  /** Get count of unanswered messages for the user. */
  unanswered_messages_count: number;
  centrifugo: CentrifugoToken | null;
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

/**
 * Nested serializer for Centrifugo WebSocket connection token.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoToken {
  /** JWT token for Centrifugo WebSocket connection */
  token: string;
  /** Centrifugo WebSocket URL */
  centrifugo_url: string;
  /** Token expiration time (ISO 8601) */
  expires_at: string;
  /** List of allowed channels for this user */
  channels: Array<string>;
}

