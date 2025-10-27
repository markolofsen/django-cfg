import { BaseAPIClient } from '../base.mjs';

/**
 * Support API Client
 * Auto-generated from OpenAPI schema
 * @module support
 * @extends BaseAPIClient
 */
export class SupportAPI extends BaseAPIClient {
    /**
     * Initialize support API client
     * @param {string} [baseURL] - Optional base URL
     */
    constructor(baseURL) {
        super(baseURL);
    }

    /**
     * supportTicketsList     * ViewSet for managing support tickets.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedTicketList>} Response data
     */
    async supportTicketsList(params = {}) {
        const path = `/cfg/support/tickets/`;        return this.get(path, params);    }
    /**
     * supportTicketsCreate     * ViewSet for managing support tickets.     * @param {TicketRequest} data - Request body     * @returns {Promise<Ticket>} Response data
     */
    async supportTicketsCreate(data) {
        const path = `/cfg/support/tickets/`;        return this.post(path, data);    }
    /**
     * supportTicketsMessagesList     * ViewSet for managing support messages.     * @param {string} ticket_uuid - UUID of the ticket     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedMessageList>} Response data
     */
    async supportTicketsMessagesList(ticket_uuid, params = {}) {
        const path = `/cfg/support/tickets/${ticket_uuid}/messages/`;        return this.get(path, params);    }
    /**
     * supportTicketsMessagesCreate     * ViewSet for managing support messages.     * @param {string} ticket_uuid - UUID of the ticket     * @param {MessageCreateRequest} data - Request body     * @returns {Promise<MessageCreate>} Response data
     */
    async supportTicketsMessagesCreate(ticket_uuid, data) {
        const path = `/cfg/support/tickets/${ticket_uuid}/messages/`;        return this.post(path, data);    }
    /**
     * supportTicketsMessagesRetrieve     * ViewSet for managing support messages.     * @param {string} ticket_uuid - UUID of the ticket     * @param {string} uuid - UUID of the message     * @returns {Promise<Message>} Response data
     */
    async supportTicketsMessagesRetrieve(ticket_uuid, uuid) {
        const path = `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`;        return this.get(path);    }
    /**
     * supportTicketsMessagesUpdate     * ViewSet for managing support messages.     * @param {string} ticket_uuid - UUID of the ticket     * @param {string} uuid - UUID of the message     * @param {MessageRequest} data - Request body     * @returns {Promise<Message>} Response data
     */
    async supportTicketsMessagesUpdate(ticket_uuid, uuid, data) {
        const path = `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`;        return this.put(path, data);    }
    /**
     * supportTicketsMessagesPartialUpdate     * ViewSet for managing support messages.     * @param {string} ticket_uuid - UUID of the ticket     * @param {string} uuid - UUID of the message     * @param {PatchedMessageRequest} data - Request body     * @returns {Promise<Message>} Response data
     */
    async supportTicketsMessagesPartialUpdate(ticket_uuid, uuid, data) {
        const path = `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`;        return this.patch(path, data);    }
    /**
     * supportTicketsMessagesDestroy     * ViewSet for managing support messages.     * @param {string} ticket_uuid - UUID of the ticket     * @param {string} uuid - UUID of the message     * @returns {Promise<void>} No content
     */
    async supportTicketsMessagesDestroy(ticket_uuid, uuid) {
        const path = `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`;        return this.delete(path);    }
    /**
     * supportTicketsRetrieve     * ViewSet for managing support tickets.     * @param {string} uuid - A UUID string identifying this ticket.     * @returns {Promise<Ticket>} Response data
     */
    async supportTicketsRetrieve(uuid) {
        const path = `/cfg/support/tickets/${uuid}/`;        return this.get(path);    }
    /**
     * supportTicketsUpdate     * ViewSet for managing support tickets.     * @param {string} uuid - A UUID string identifying this ticket.     * @param {TicketRequest} data - Request body     * @returns {Promise<Ticket>} Response data
     */
    async supportTicketsUpdate(uuid, data) {
        const path = `/cfg/support/tickets/${uuid}/`;        return this.put(path, data);    }
    /**
     * supportTicketsPartialUpdate     * ViewSet for managing support tickets.     * @param {string} uuid - A UUID string identifying this ticket.     * @param {PatchedTicketRequest} data - Request body     * @returns {Promise<Ticket>} Response data
     */
    async supportTicketsPartialUpdate(uuid, data) {
        const path = `/cfg/support/tickets/${uuid}/`;        return this.patch(path, data);    }
    /**
     * supportTicketsDestroy     * ViewSet for managing support tickets.     * @param {string} uuid - A UUID string identifying this ticket.     * @returns {Promise<void>} No content
     */
    async supportTicketsDestroy(uuid) {
        const path = `/cfg/support/tickets/${uuid}/`;        return this.delete(path);    }
}

// Default instance for convenience
export const supportAPI = new SupportAPI();

// Default export
export default SupportAPI;