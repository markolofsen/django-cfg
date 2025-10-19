/**
 * Payments Service
 *
 * Manages payment operations - create, check status, confirm
 */

import { BaseClient } from '../../BaseClient';
import { APIError, CfgPaymentsTypes } from '../../generated';

export class PaymentsService extends BaseClient {
  /**
   * List payments
   */
  static async list(params?: {
    page?: number;
    page_size?: number;
  }): Promise<{
    success: boolean;
    payments?: CfgPaymentsTypes.PaginatedPaymentListList;
    error?: string;
  }> {
    try {
      const response = await this.api.cfg_payments.paymentsList(
        params?.page,
        params?.page_size
      );
      return { success: true, payments: response };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Create payment
   */
  static async create(): Promise<{
    success: boolean;
    payment?: any;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const response = await this.api.cfg_payments.paymentsCreateCreate();
      return { success: true, payment: response };
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
   * Get payment details
   */
  static async get(id: string): Promise<{
    success: boolean;
    payment?: CfgPaymentsTypes.PaymentDetail;
    error?: string;
  }> {
    try {
      const payment = await this.api.cfg_payments.paymentsRetrieve(id);
      return { success: true, payment };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Get payment status
   */
  static async getStatus(id: string): Promise<{
    success: boolean;
    payment?: any;
    error?: string;
  }> {
    try {
      const payment = await this.api.cfg_payments.paymentsStatusRetrieve(id);
      return { success: true, payment };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Confirm payment (user clicked "I paid")
   */
  static async confirm(id: string): Promise<{
    success: boolean;
    payment?: any;
    error?: string;
  }> {
    try {
      const payment = await this.api.cfg_payments.paymentsConfirmCreate(id);
      return { success: true, payment };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * @deprecated Cancel payment removed in v2.0
   */
  static async cancel(): Promise<{
    success: boolean;
    payment?: never;
    error?: string;
  }> {
    return { success: false, error: 'Cancel payment removed in v2.0' };
  }

  /**
   * @deprecated Check status method replaced with getStatus in v2.0
   */
  static async checkStatus(id: string): Promise<{
    success: boolean;
    payment?: any;
    error?: string;
  }> {
    return this.getStatus(id);
  }

  /**
   * @deprecated Analytics removed in v2.0
   */
  static async getAnalytics(): Promise<{
    success: boolean;
    analytics?: never;
    error?: string;
  }> {
    return { success: false, error: 'Analytics removed in v2.0' };
  }

  /**
   * @deprecated Stats removed in v2.0
   */
  static async getStats(): Promise<{
    success: boolean;
    stats?: never;
    error?: string;
  }> {
    return { success: false, error: 'Stats removed in v2.0' };
  }
}
