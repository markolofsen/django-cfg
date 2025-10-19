/**
 * Support Layout Types
 * Types for SupportLayout - combines API types with UI state
 */

import type { Ticket, Message } from '@djangocfg/api/cfg/contexts';

// Re-export API types
export type { Ticket, Message };

// UI State
export interface SupportUIState {
  selectedTicketUuid: string | null;
  isCreateDialogOpen: boolean;
  viewMode: 'list' | 'grid';
}

// Form types
export interface TicketFormData {
  subject: string;
  message: string;
}

