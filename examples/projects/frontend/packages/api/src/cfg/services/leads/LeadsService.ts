/**
 * Leads Service
 *
 * Handles lead submission and management
 */

import { BaseClient } from '../../BaseClient';
import { APIError, CfgLeadsTypes, CfgLeadSubmissionTypes, Enums } from '../../generated';

export class LeadsService extends BaseClient {
  /**
   * Submit lead (public)
   */
  static async submitLead(data: {
    email: string;
    name: string;
    message: string;
    company?: string;
    phone?: string;
    contact_type?: Enums.LeadSubmissionRequestContactType;
  }): Promise<{
    success: boolean;
    lead?: CfgLeadSubmissionTypes.LeadSubmissionResponse;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const lead = await this.api.cfg_lead_submission.leadsSubmitCreate({
        name: data.name,
        email: data.email,
        message: data.message,
        company: data.company,
        contact_type: data.contact_type || Enums.LeadSubmissionRequestContactType.EMAIL,
        contact_value: data.phone,
        site_url: typeof window !== 'undefined' ? window.location.href : '',
      });
      return { success: true, lead };
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
   * Get leads list (admin)
   */
  static async getLeads(
    page: number = 1,
    pageSize: number = 20
  ): Promise<{
    success: boolean;
    leads?: CfgLeadsTypes.PaginatedLeadSubmissionList;
    error?: string;
  }> {
    try {
      const response = await this.api.cfg_leads.list({ page, page_size: pageSize });
      return { success: true, leads: response };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Get lead by ID (admin)
   */
  static async getLead(id: number): Promise<{
    success: boolean;
    lead?: CfgLeadsTypes.LeadSubmission;
    error?: string;
  }> {
    try {
      const lead = await this.api.cfg_leads.retrieve(id);
      return { success: true, lead };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Update lead (admin)
   */
  static async updateLead(
    id: number,
    data: CfgLeadsTypes.PatchedLeadSubmissionRequest
  ): Promise<{
    success: boolean;
    lead?: CfgLeadsTypes.LeadSubmission;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    try {
      const lead = await this.api.cfg_leads.partialUpdate(id, data);
      return { success: true, lead };
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
   * Delete lead (admin)
   */
  static async deleteLead(id: number): Promise<{
    success: boolean;
    error?: string;
  }> {
    try {
      await this.api.cfg_leads.destroy(id);
      return { success: true };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }
}
