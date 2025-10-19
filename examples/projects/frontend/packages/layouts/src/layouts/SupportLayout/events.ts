/**
 * Support Layout Events
 * Event system for SupportLayout
 */

export const SUPPORT_LAYOUT_EVENTS = {
  // Dialog events
  OPEN_CREATE_DIALOG: 'support-layout:open-create-dialog',
  CLOSE_CREATE_DIALOG: 'support-layout:close-create-dialog',
  
  // Ticket events
  TICKET_SELECTED: 'support-layout:ticket-selected',
  TICKET_CREATED: 'support-layout:ticket-created',
  
  // Message events
  MESSAGE_SENT: 'support-layout:message-sent',
} as const;

// Event publishers
export const openCreateTicketDialog = () => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent(SUPPORT_LAYOUT_EVENTS.OPEN_CREATE_DIALOG));
  }
};

export const closeCreateTicketDialog = () => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent(SUPPORT_LAYOUT_EVENTS.CLOSE_CREATE_DIALOG));
  }
};

