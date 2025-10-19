/**
 * Newsletter Service
 *
 * Manages newsletter subscriptions
 */

import { BaseClient } from '../../BaseClient';
import { APIError, CfgSubscriptionsTypes } from '../../generated';

export class NewsletterService extends BaseClient {
  /**
   * Subscribe to newsletter
   */
  static async subscribe(
    data: CfgSubscriptionsTypes.SubscribeRequest
  ): Promise<{
    success: boolean;
    response?: CfgSubscriptionsTypes.SubscribeResponse;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const response = await this.api.cfg_subscriptions.newsletterSubscribeCreate(data);
      return { success: true, response };
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
   * Unsubscribe from newsletter
   */
  static async unsubscribe(
    data: CfgSubscriptionsTypes.UnsubscribeRequest
  ): Promise<{
    success: boolean;
    response?: CfgSubscriptionsTypes.SuccessResponse;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const response = await this.api.cfg_subscriptions.newsletterUnsubscribeCreate(data);
      return { success: true, response };
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
   * List user subscriptions
   */
  static async list(page?: number, pageSize?: number): Promise<{
    success: boolean;
    subscriptions?: CfgSubscriptionsTypes.PaginatedNewsletterSubscriptionList;
    error?: string;
  }> {
    try {
      const response = await this.api.cfg_subscriptions.newsletterSubscriptionsList(page, pageSize);
      return { success: true, subscriptions: response };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }
}
