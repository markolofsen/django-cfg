import * as Models from "./models";


/**
 * API endpoints for Support.
 */
export class CfgSupport {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async ticketsList(page?: number, page_size?: number): Promise<Models.PaginatedTicketList>;
  async ticketsList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedTicketList>;

  /**
   * ViewSet for managing support tickets. Requires authenticated user (JWT
   * or Session). Staff users can see all tickets, regular users see only
   * their own.
   */
  async ticketsList(...args: any[]): Promise<Models.PaginatedTicketList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/support/tickets/", { params });
    return response;
  }

  /**
   * ViewSet for managing support tickets. Requires authenticated user (JWT
   * or Session). Staff users can see all tickets, regular users see only
   * their own.
   */
  async ticketsCreate(data: Models.TicketRequest): Promise<Models.Ticket> {
    const response = await this.client.request('POST', "/cfg/support/tickets/", { body: data });
    return response;
  }

  async ticketsMessagesList(ticket_uuid: string, page?: number, page_size?: number): Promise<Models.PaginatedMessageList>;
  async ticketsMessagesList(ticket_uuid: string, params?: { page?: number; page_size?: number }): Promise<Models.PaginatedMessageList>;

  /**
   * ViewSet for managing support messages. Requires authenticated user (JWT
   * or Session). Users can only access messages for their own tickets.
   */
  async ticketsMessagesList(...args: any[]): Promise<Models.PaginatedMessageList> {
    const ticket_uuid = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { page: args[1], page_size: args[2] };
    }
    const response = await this.client.request('GET', `/cfg/support/tickets/${ticket_uuid}/messages/`, { params });
    return response;
  }

  /**
   * ViewSet for managing support messages. Requires authenticated user (JWT
   * or Session). Users can only access messages for their own tickets.
   */
  async ticketsMessagesCreate(ticket_uuid: string, data: Models.MessageCreateRequest): Promise<Models.MessageCreate> {
    const response = await this.client.request('POST', `/cfg/support/tickets/${ticket_uuid}/messages/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages. Requires authenticated user (JWT
   * or Session). Users can only access messages for their own tickets.
   */
  async ticketsMessagesRetrieve(ticket_uuid: string, uuid: string): Promise<Models.Message> {
    const response = await this.client.request('GET', `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`);
    return response;
  }

  /**
   * ViewSet for managing support messages. Requires authenticated user (JWT
   * or Session). Users can only access messages for their own tickets.
   */
  async ticketsMessagesUpdate(ticket_uuid: string, uuid: string, data: Models.MessageRequest): Promise<Models.Message> {
    const response = await this.client.request('PUT', `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages. Requires authenticated user (JWT
   * or Session). Users can only access messages for their own tickets.
   */
  async ticketsMessagesPartialUpdate(ticket_uuid: string, uuid: string, data?: Models.PatchedMessageRequest): Promise<Models.Message> {
    const response = await this.client.request('PATCH', `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages. Requires authenticated user (JWT
   * or Session). Users can only access messages for their own tickets.
   */
  async ticketsMessagesDestroy(ticket_uuid: string, uuid: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`);
    return;
  }

  /**
   * ViewSet for managing support tickets. Requires authenticated user (JWT
   * or Session). Staff users can see all tickets, regular users see only
   * their own.
   */
  async ticketsRetrieve(uuid: string): Promise<Models.Ticket> {
    const response = await this.client.request('GET', `/cfg/support/tickets/${uuid}/`);
    return response;
  }

  /**
   * ViewSet for managing support tickets. Requires authenticated user (JWT
   * or Session). Staff users can see all tickets, regular users see only
   * their own.
   */
  async ticketsUpdate(uuid: string, data: Models.TicketRequest): Promise<Models.Ticket> {
    const response = await this.client.request('PUT', `/cfg/support/tickets/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support tickets. Requires authenticated user (JWT
   * or Session). Staff users can see all tickets, regular users see only
   * their own.
   */
  async ticketsPartialUpdate(uuid: string, data?: Models.PatchedTicketRequest): Promise<Models.Ticket> {
    const response = await this.client.request('PATCH', `/cfg/support/tickets/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support tickets. Requires authenticated user (JWT
   * or Session). Staff users can see all tickets, regular users see only
   * their own.
   */
  async ticketsDestroy(uuid: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/support/tickets/${uuid}/`);
    return;
  }

}