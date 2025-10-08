import * as Models from "./models";


/**
 * API endpoints for Support.
 */
export class CfgSupportAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async ticketsList(): Promise<void> {
    const response = await this.client.request('GET', "/django_cfg_support/tickets/");
    return;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async ticketsCreate(data: Models.TicketRequest): Promise<Models.Ticket> {
    const response = await this.client.request('POST', "/django_cfg_support/tickets/", { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages.
   */
  async ticketsMessagesList(ticket_uuid: string): Promise<void> {
    const response = await this.client.request('GET', `/django_cfg_support/tickets/${ticket_uuid}/messages/`);
    return;
  }

  /**
   * ViewSet for managing support messages.
   */
  async ticketsMessagesCreate(ticket_uuid: string, data: Models.MessageCreateRequest): Promise<Models.MessageCreate> {
    const response = await this.client.request('POST', `/django_cfg_support/tickets/${ticket_uuid}/messages/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages.
   */
  async ticketsMessagesRetrieve(ticket_uuid: string, uuid: string): Promise<Models.Message> {
    const response = await this.client.request('GET', `/django_cfg_support/tickets/${ticket_uuid}/messages/${uuid}/`);
    return response;
  }

  /**
   * ViewSet for managing support messages.
   */
  async ticketsMessagesUpdate(ticket_uuid: string, uuid: string, data: Models.MessageRequest): Promise<Models.Message> {
    const response = await this.client.request('PUT', `/django_cfg_support/tickets/${ticket_uuid}/messages/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages.
   */
  async ticketsMessagesPartialUpdate(ticket_uuid: string, uuid: string, data?: Models.PatchedMessageRequest): Promise<Models.Message> {
    const response = await this.client.request('PATCH', `/django_cfg_support/tickets/${ticket_uuid}/messages/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support messages.
   */
  async ticketsMessagesDestroy(ticket_uuid: string, uuid: string): Promise<void> {
    const response = await this.client.request('DELETE', `/django_cfg_support/tickets/${ticket_uuid}/messages/${uuid}/`);
    return;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async ticketsRetrieve(uuid: string): Promise<Models.Ticket> {
    const response = await this.client.request('GET', `/django_cfg_support/tickets/${uuid}/`);
    return response;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async ticketsUpdate(uuid: string, data: Models.TicketRequest): Promise<Models.Ticket> {
    const response = await this.client.request('PUT', `/django_cfg_support/tickets/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async ticketsPartialUpdate(uuid: string, data?: Models.PatchedTicketRequest): Promise<Models.Ticket> {
    const response = await this.client.request('PATCH', `/django_cfg_support/tickets/${uuid}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for managing support tickets.
   */
  async ticketsDestroy(uuid: string): Promise<void> {
    const response = await this.client.request('DELETE', `/django_cfg_support/tickets/${uuid}/`);
    return;
  }

}