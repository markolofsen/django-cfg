import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedTicketList {
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
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<Ticket>;
}

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
 * Response model (includes read-only fields).
 */
export interface PaginatedMessageList {
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
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<Message>;
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
  avatar: string | null;
  /** Get user's initials for avatar fallback. */
  initials: string;
  /** Designates whether the user can log into this admin site. */
  is_staff: boolean;
  /** Designates that this user has all permissions without explicitly assigning them. */
  is_superuser: boolean;
}

