import * as Enums from "../enums";

/**
 * 
 * Request model (no read-only fields).
 */
export interface TicketRequest {
  user: number;
  subject: string;
  /** * `open` - Open
  * `waiting_for_user` - Waiting for User
  * `waiting_for_admin` - Waiting for Admin
  * `resolved` - Resolved
  * `closed` - Closed */
  status?: Enums.TicketRequestStatus;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface Ticket {
  uuid: string;
  user: number;
  subject: string;
  /** * `open` - Open
  * `waiting_for_user` - Waiting for User
  * `waiting_for_admin` - Waiting for Admin
  * `resolved` - Resolved
  * `closed` - Closed */
  status?: Enums.TicketStatus;
  created_at: string;
  /** Get count of unanswered messages for this specific ticket. */
  unanswered_messages_count: number;
}

/**
 * 
 * Request model (no read-only fields).
 */
export interface MessageCreateRequest {
  text: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface MessageCreate {
  text: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface Message {
  uuid: string;
  ticket: string;
  sender: Record<string, any>;
  /** Check if this message is from the ticket author. */
  is_from_author: boolean;
  text: string;
  created_at: string;
}

/**
 * 
 * Request model (no read-only fields).
 */
export interface MessageRequest {
  text: string;
}

/**
 * 
 * Request model (no read-only fields).
 */
export interface PatchedMessageRequest {
  text?: string;
}

/**
 * 
 * Request model (no read-only fields).
 */
export interface PatchedTicketRequest {
  user?: number;
  subject?: string;
  /** * `open` - Open
  * `waiting_for_user` - Waiting for User
  * `waiting_for_admin` - Waiting for Admin
  * `resolved` - Resolved
  * `closed` - Closed */
  status?: Enums.PatchedTicketRequestStatus;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface Sender {
  id: number;
  /** Get formatted username for display. */
  display_username: string;
  email: string;
  avatar?: string;
  /** Get user's initials for avatar fallback. */
  initials: string;
  /** Designates whether the user can log into this admin site. */
  is_staff: boolean;
  /** Designates that this user has all permissions without explicitly assigning them. */
  is_superuser: boolean;
}

