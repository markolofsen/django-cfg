import * as Enums from "../enums";

/**
 * Serializer for OTP request.
 * 
 * Request model (no read-only fields).
 */
export interface OTPRequestRequest {
  /** Email address or phone number for OTP delivery */
  identifier: string;
  /** Delivery channel: 'email' or 'phone'. Auto-detected if not provided.

  * `email` - Email
  * `phone` - Phone */
  channel?: Enums.OTPRequestRequestChannel;
  /** Source URL for tracking registration (e.g., https://dashboard.unrealon.com) */
  source_url?: string;
}

/**
 * OTP request response.
 * 
 * Response model (includes read-only fields).
 */
export interface OTPRequestResponse {
  /** Success message */
  message: string;
}

/**
 * Error response for OTP operations.
 * 
 * Response model (includes read-only fields).
 */
export interface OTPErrorResponse {
  /** Error message */
  error: string;
}

/**
 * Serializer for OTP verification.
 * 
 * Request model (no read-only fields).
 */
export interface OTPVerifyRequest {
  /** Email address or phone number used for OTP request */
  identifier: string;
  otp: string;
  /** Delivery channel: 'email' or 'phone'. Auto-detected if not provided.

  * `email` - Email
  * `phone` - Phone */
  channel?: Enums.OTPVerifyRequestChannel;
  /** Source URL for tracking login (e.g., https://dashboard.unrealon.com) */
  source_url?: string;
}

/**
 * OTP verification response.
 * 
 * Response model (includes read-only fields).
 */
export interface OTPVerifyResponse {
  /** JWT refresh token */
  refresh: string;
  /** JWT access token */
  access: string;
  user: User;
}

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

