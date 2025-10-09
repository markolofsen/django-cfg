import * as Models from "./models";


/**
 * API endpoints for Cfg Support.
 */
export class CfgSupportAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async cfgSupportTicketsList(): Promise<void> {
    const response = await this.client.request('GET', "/cfg/support/tickets/");
    return;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async cfgSupportTicketsCreate(data: Models.TicketRequest): Promise<Models.Ticket> {
    const response = await this.client.request('POST', "/cfg/support/tickets/", { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages.
   */
  async cfgSupportTicketsMessagesList(ticket_uuid: string): Promise<void> {
    const response = await this.client.request('GET', `/cfg/support/tickets/${ticket_uuid}/messages/`);
    return;
  }

  /**
   * ViewSet for managing support messages.
   */
  async cfgSupportTicketsMessagesCreate(ticket_uuid: string, data: Models.MessageCreateRequest): Promise<Models.MessageCreate> {
    const response = await this.client.request('POST', `/cfg/support/tickets/${ticket_uuid}/messages/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages.
   */
  async cfgSupportTicketsMessagesRetrieve(ticket_uuid: string, uuid: string): Promise<Models.Message> {
    const response = await this.client.request('GET', `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`);
    return response;
  }

  /**
   * ViewSet for managing support messages.
   */
  async cfgSupportTicketsMessagesUpdate(ticket_uuid: string, uuid: string, data: Models.MessageRequest): Promise<Models.Message> {
    const response = await this.client.request('PUT', `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages.
   */
  async cfgSupportTicketsMessagesPartialUpdate(ticket_uuid: string, uuid: string, data?: Models.PatchedMessageRequest): Promise<Models.Message> {
    const response = await this.client.request('PATCH', `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages.
   */
  async cfgSupportTicketsMessagesDestroy(ticket_uuid: string, uuid: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/support/tickets/${ticket_uuid}/messages/${uuid}/`);
    return;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async cfgSupportTicketsRetrieve(uuid: string): Promise<Models.Ticket> {
    const response = await this.client.request('GET', `/cfg/support/tickets/${uuid}/`);
    return response;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async cfgSupportTicketsUpdate(uuid: string, data: Models.TicketRequest): Promise<Models.Ticket> {
    const response = await this.client.request('PUT', `/cfg/support/tickets/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async cfgSupportTicketsPartialUpdate(uuid: string, data?: Models.PatchedTicketRequest): Promise<Models.Ticket> {
    const response = await this.client.request('PATCH', `/cfg/support/tickets/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async cfgSupportTicketsDestroy(uuid: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/support/tickets/${uuid}/`);
    return;
  }

}