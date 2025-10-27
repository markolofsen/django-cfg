import { BaseAPIClient } from '../base.mjs';

/**
 * Leads API Client
 * Auto-generated from OpenAPI schema
 * @module leads
 * @extends BaseAPIClient
 */
export class LeadsAPI extends BaseAPIClient {
    /**
     * Initialize leads API client
     * @param {string} [baseURL] - Optional base URL
     */
    constructor(baseURL) {
        super(baseURL);
    }

    /**
     * leadsList     * ViewSet for Lead model.

Provides only submission functionality for leads from frontend forms.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedLeadSubmissionList>} Response data
     */
    async leadsList(params = {}) {
        const path = `/cfg/leads/`;        return this.get(path, params);    }
    /**
     * leadsCreate     * ViewSet for Lead model.

Provides only submission functionality for leads from frontend forms.     * @param {LeadSubmissionRequest} data - Request body     * @returns {Promise<LeadSubmission>} Response data
     */
    async leadsCreate(data) {
        const path = `/cfg/leads/`;        return this.post(path, data);    }
    /**
     * leadsRetrieve     * ViewSet for Lead model.

Provides only submission functionality for leads from frontend forms.     * @param {number} id - A unique integer value identifying this Lead.     * @returns {Promise<LeadSubmission>} Response data
     */
    async leadsRetrieve(id) {
        const path = `/cfg/leads/${id}/`;        return this.get(path);    }
    /**
     * leadsUpdate     * ViewSet for Lead model.

Provides only submission functionality for leads from frontend forms.     * @param {number} id - A unique integer value identifying this Lead.     * @param {LeadSubmissionRequest} data - Request body     * @returns {Promise<LeadSubmission>} Response data
     */
    async leadsUpdate(id, data) {
        const path = `/cfg/leads/${id}/`;        return this.put(path, data);    }
    /**
     * leadsPartialUpdate     * ViewSet for Lead model.

Provides only submission functionality for leads from frontend forms.     * @param {number} id - A unique integer value identifying this Lead.     * @param {PatchedLeadSubmissionRequest} data - Request body     * @returns {Promise<LeadSubmission>} Response data
     */
    async leadsPartialUpdate(id, data) {
        const path = `/cfg/leads/${id}/`;        return this.patch(path, data);    }
    /**
     * leadsDestroy     * ViewSet for Lead model.

Provides only submission functionality for leads from frontend forms.     * @param {number} id - A unique integer value identifying this Lead.     * @returns {Promise<void>} No content
     */
    async leadsDestroy(id) {
        const path = `/cfg/leads/${id}/`;        return this.delete(path);    }
    /**
     * Submit Lead Form     * Submit a new lead from frontend contact form with automatic Telegram notifications.     * @param {LeadSubmissionRequest} data - Request body     * @returns {Promise<LeadSubmissionResponse>} Response data
     */
    async leadsSubmitCreate(data) {
        const path = `/cfg/leads/submit/`;        return this.post(path, data);    }
}

// Default instance for convenience
export const leadsAPI = new LeadsAPI();

// Default export
export default LeadsAPI;