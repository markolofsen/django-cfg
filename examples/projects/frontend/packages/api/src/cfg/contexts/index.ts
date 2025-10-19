/**
 * CFG API Contexts
 * 
 * Centralized React contexts for all CFG API modules
 * Uses generated SWR hooks for optimal data fetching and caching
 */

// Accounts (Auth & Profile)
export { 
  AccountsProvider, 
  useAccountsContext,
  PatchedUserProfileUpdateRequestSchema
} from './AccountsContext';
export type { 
  AccountsContextValue,
  PatchedUserProfileUpdateRequest
} from './AccountsContext';

// Newsletter (Campaigns & Subscriptions)
export { NewsletterProvider, useNewsletterContext } from './NewsletterContext';
export type { NewsletterContextValue } from './NewsletterContext';

// Leads (Lead Submissions)
export { LeadsProvider, useLeadsContext } from './LeadsContext';
export type { LeadsContextValue } from './LeadsContext';

// Support (Tickets & Messages)
export { 
  SupportProvider, 
  useSupportContext 
} from './SupportContext';
export type { 
  SupportContextValue,
  Ticket,
  TicketRequest,
  PatchedTicketRequest,
  Message,
  MessageRequest,
  MessageCreateRequest,
  PatchedMessageRequest,
} from './SupportContext';

// Payments (Payments, Balances, Currencies, API Keys, Overview)
export * from './payments';

// Knowbase (Chat, Documents, Sessions)
export * from './knowbase';

