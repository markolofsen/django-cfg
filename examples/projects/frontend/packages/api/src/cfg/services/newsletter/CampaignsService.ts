/**
 * Newsletter Campaigns Service
 *
 * Manages newsletter campaigns
 */

import { BaseClient } from '../../BaseClient';
import { APIError, CfgCampaignsTypes } from '../../generated';

export class CampaignsService extends BaseClient {
  /**
   * List campaigns
   */
  static async list(page?: number, pageSize?: number): Promise<{
    success: boolean;
    campaigns?: CfgCampaignsTypes.PaginatedNewsletterCampaignList;
    error?: string;
  }> {
    try {
      const response = await this.api.cfg_campaigns.newsletterCampaignsList(page, pageSize);
      return { success: true, campaigns: response };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Create campaign
   */
  static async create(
    data: CfgCampaignsTypes.NewsletterCampaignRequest
  ): Promise<{
    success: boolean;
    campaign?: CfgCampaignsTypes.NewsletterCampaign;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const campaign = await this.api.cfg_campaigns.newsletterCampaignsCreate(data);
      return { success: true, campaign };
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
   * Get campaign details
   */
  static async get(id: number): Promise<{
    success: boolean;
    campaign?: CfgCampaignsTypes.NewsletterCampaign;
    error?: string;
  }> {
    try {
      const campaign = await this.api.cfg_campaigns.newsletterCampaignsRetrieve(id);
      return { success: true, campaign };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Update campaign
   */
  static async update(
    id: number,
    data: CfgCampaignsTypes.NewsletterCampaignRequest
  ): Promise<{
    success: boolean;
    campaign?: CfgCampaignsTypes.NewsletterCampaign;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const campaign = await this.api.cfg_campaigns.newsletterCampaignsUpdate(id, data);
      return { success: true, campaign };
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
   * Delete campaign
   */
  static async delete(id: number): Promise<{
    success: boolean;
    error?: string;
  }> {
    try {
      await this.api.cfg_campaigns.newsletterCampaignsDestroy(id);
      return { success: true };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Send campaign
   */
  static async send(
    data: CfgCampaignsTypes.SendCampaignRequest
  ): Promise<{
    success: boolean;
    response?: CfgCampaignsTypes.SendCampaignResponse;
    error?: string;
  }> {
    try {
      const response = await this.api.cfg_campaigns.newsletterCampaignsSendCreate(data);
      return { success: true, response };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }
}
