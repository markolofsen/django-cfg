/**
 * Support Service
 *
 * Handles support tickets and messages
 */

import { BaseClient } from '../../BaseClient';
import { APIError, CfgSupportTypes } from '../../generated';

export class SupportService extends BaseClient {
  /**
   * Get tickets list
   */
  static async getTickets(): Promise<{
    success: boolean;
    error?: string;
  }> {
    try {
      await this.api.cfg_support.ticketsList();
      return { success: true };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Get ticket by ID
   */
  static async getTicket(id: string): Promise<{
    success: boolean;
    ticket?: CfgSupportTypes.Ticket;
    error?: string;
  }> {
    try {
      const ticket = await this.api.cfg_support.ticketsRetrieve(id);
      return { success: true, ticket };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Create ticket
   */
  static async createTicket(data: CfgSupportTypes.TicketRequest): Promise<{
    success: boolean;
    ticket?: CfgSupportTypes.Ticket;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const ticket = await this.api.cfg_support.ticketsCreate(data);
      return { success: true, ticket };
    } catch (error) {
      if (error instanceof APIError) {
        if (error.isValidationError && error.fieldErrors) {
          return { success: false, fieldErrors: error.fieldErrors };
        }
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Update ticket
   */
  static async updateTicket(
    id: string,
    data: CfgSupportTypes.PatchedTicketRequest
  ): Promise<{
    success: boolean;
    ticket?: CfgSupportTypes.Ticket;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const ticket = await this.api.cfg_support.ticketsPartialUpdate(id, data);
      return { success: true, ticket };
    } catch (error) {
      if (error instanceof APIError) {
        if (error.isValidationError && error.fieldErrors) {
          return { success: false, fieldErrors: error.fieldErrors };
        }
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Get ticket messages
   */
  static async getMessages(ticketId: string): Promise<{
    success: boolean;
    error?: string;
  }> {
    try {
      await this.api.cfg_support.ticketsMessagesList(ticketId);
      return { success: true };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Send message to ticket
   */
  static async sendMessage(
    ticketId: string,
    text: string
  ): Promise<{
    success: boolean;
    message?: CfgSupportTypes.MessageCreate;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const message = await this.api.cfg_support.ticketsMessagesCreate(ticketId, {
        text,
      });
      return { success: true, message };
    } catch (error) {
      if (error instanceof APIError) {
        if (error.isValidationError && error.fieldErrors) {
          return { success: false, fieldErrors: error.fieldErrors };
        }
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }
}
