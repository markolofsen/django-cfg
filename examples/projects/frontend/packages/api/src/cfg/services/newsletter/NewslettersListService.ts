/**
 * Newsletters List Service
 *
 * Manages available newsletters
 */

import { BaseClient } from '../../BaseClient';
import { APIError, CfgNewslettersTypes } from '../../generated';

export class NewslettersListService extends BaseClient {
  /**
   * List available newsletters
   */
  static async list(page?: number, pageSize?: number): Promise<{
    success: boolean;
    newsletters?: CfgNewslettersTypes.PaginatedNewsletterList;
    error?: string;
  }> {
    try {
      const response = await this.api.cfg_newsletters.newsletterNewslettersList({ page, page_size: pageSize });
      return { success: true, newsletters: response };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Get newsletter details
   */
  static async get(id: number): Promise<{
    success: boolean;
    newsletter?: CfgNewslettersTypes.Newsletter;
    error?: string;
  }> {
    try {
      const newsletter = await this.api.cfg_newsletters.newsletterNewslettersRetrieve(id);
      return { success: true, newsletter };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }
}
