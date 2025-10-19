/**
 * Bulk Email Service
 *
 * Sends bulk emails
 */

import { BaseClient } from '../../BaseClient';
import { APIError, CfgBulkEmailTypes } from '../../generated';

export class BulkEmailService extends BaseClient {
  /**
   * Send bulk email
   */
  static async send(
    data: CfgBulkEmailTypes.BulkEmailRequest
  ): Promise<{
    success: boolean;
    response?: CfgBulkEmailTypes.BulkEmailResponse;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const response = await this.api.cfg_bulk_email.newsletterBulkCreate(data);
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
}
