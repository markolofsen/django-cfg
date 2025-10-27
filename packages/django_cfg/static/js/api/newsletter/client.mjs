import { BaseAPIClient } from '../base.mjs';

/**
 * Newsletter API Client
 * Auto-generated from OpenAPI schema
 * @module newsletter
 * @extends BaseAPIClient
 */
export class NewsletterAPI extends BaseAPIClient {
    /**
     * Initialize newsletter API client
     * @param {string} [baseURL] - Optional base URL
     */
    constructor(baseURL) {
        super(baseURL);
    }

    /**
     * Send Bulk Email     * Send bulk emails to multiple recipients using base email template.     * @param {BulkEmailRequest} data - Request body     * @returns {Promise<BulkEmailResponse>} Response data
     */
    async newsletterBulkCreate(data) {
        const path = `/cfg/newsletter/bulk/`;        return this.post(path, data);    }
    /**
     * List Newsletter Campaigns     * Get a list of all newsletter campaigns.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedNewsletterCampaignList>} Response data
     */
    async newsletterCampaignsList(params = {}) {
        const path = `/cfg/newsletter/campaigns/`;        return this.get(path, params);    }
    /**
     * Create Newsletter Campaign     * Create a new newsletter campaign.     * @param {NewsletterCampaignRequest} data - Request body     * @returns {Promise<NewsletterCampaign>} Response data
     */
    async newsletterCampaignsCreate(data) {
        const path = `/cfg/newsletter/campaigns/`;        return this.post(path, data);    }
    /**
     * Get Campaign Details     * Retrieve details of a specific newsletter campaign.     * @param {number} id     * @returns {Promise<NewsletterCampaign>} Response data
     */
    async newsletterCampaignsRetrieve(id) {
        const path = `/cfg/newsletter/campaigns/${id}/`;        return this.get(path);    }
    /**
     * Update Campaign     * Update a newsletter campaign.     * @param {number} id     * @param {NewsletterCampaignRequest} data - Request body     * @returns {Promise<NewsletterCampaign>} Response data
     */
    async newsletterCampaignsUpdate(id, data) {
        const path = `/cfg/newsletter/campaigns/${id}/`;        return this.put(path, data);    }
    /**
     * newsletterCampaignsPartialUpdate     * Retrieve, update, or delete a newsletter campaign.     * @param {number} id     * @param {PatchedNewsletterCampaignRequest} data - Request body     * @returns {Promise<NewsletterCampaign>} Response data
     */
    async newsletterCampaignsPartialUpdate(id, data) {
        const path = `/cfg/newsletter/campaigns/${id}/`;        return this.patch(path, data);    }
    /**
     * Delete Campaign     * Delete a newsletter campaign.     * @param {number} id     * @returns {Promise<void>} No content
     */
    async newsletterCampaignsDestroy(id) {
        const path = `/cfg/newsletter/campaigns/${id}/`;        return this.delete(path);    }
    /**
     * Send Newsletter Campaign     * Send a newsletter campaign to all subscribers.     * @param {SendCampaignRequest} data - Request body     * @returns {Promise<SendCampaignResponse>} Response data
     */
    async newsletterCampaignsSendCreate(data) {
        const path = `/cfg/newsletter/campaigns/send/`;        return this.post(path, data);    }
    /**
     * List Email Logs     * Get a list of email sending logs.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedEmailLogList>} Response data
     */
    async newsletterLogsList(params = {}) {
        const path = `/cfg/newsletter/logs/`;        return this.get(path, params);    }
    /**
     * List Active Newsletters     * Get a list of all active newsletters available for subscription.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedNewsletterList>} Response data
     */
    async newsletterNewslettersList(params = {}) {
        const path = `/cfg/newsletter/newsletters/`;        return this.get(path, params);    }
    /**
     * Get Newsletter Details     * Retrieve details of a specific newsletter.     * @param {number} id     * @returns {Promise<Newsletter>} Response data
     */
    async newsletterNewslettersRetrieve(id) {
        const path = `/cfg/newsletter/newsletters/${id}/`;        return this.get(path);    }
    /**
     * Subscribe to Newsletter     * Subscribe an email address to a newsletter.     * @param {SubscribeRequest} data - Request body     * @returns {Promise<SubscribeResponse>} Response data
     */
    async newsletterSubscribeCreate(data) {
        const path = `/cfg/newsletter/subscribe/`;        return this.post(path, data);    }
    /**
     * List User Subscriptions     * Get a list of current user's active newsletter subscriptions.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedNewsletterSubscriptionList>} Response data
     */
    async newsletterSubscriptionsList(params = {}) {
        const path = `/cfg/newsletter/subscriptions/`;        return this.get(path, params);    }
    /**
     * Test Email Sending     * Send a test email to verify mailer configuration.     * @param {TestEmailRequest} data - Request body     * @returns {Promise<BulkEmailResponse>} Response data
     */
    async newsletterTestCreate(data) {
        const path = `/cfg/newsletter/test/`;        return this.post(path, data);    }
    /**
     * Unsubscribe from Newsletter     * Unsubscribe from a newsletter using subscription ID.     * @param {UnsubscribeRequest} data - Request body     * @returns {Promise<SuccessResponse>} Response data
     */
    async newsletterUnsubscribeCreate(data) {
        const path = `/cfg/newsletter/unsubscribe/`;        return this.post(path, data);    }
    /**
     * newsletterUnsubscribeUpdate     * Handle newsletter unsubscriptions.     * @param {UnsubscribeRequest} data - Request body     * @returns {Promise<Unsubscribe>} Response data
     */
    async newsletterUnsubscribeUpdate(data) {
        const path = `/cfg/newsletter/unsubscribe/`;        return this.put(path, data);    }
    /**
     * newsletterUnsubscribePartialUpdate     * Handle newsletter unsubscriptions.     * @param {PatchedUnsubscribeRequest} data - Request body     * @returns {Promise<Unsubscribe>} Response data
     */
    async newsletterUnsubscribePartialUpdate(data) {
        const path = `/cfg/newsletter/unsubscribe/`;        return this.patch(path, data);    }
}

// Default instance for convenience
export const newsletterAPI = new NewsletterAPI();

// Default export
export default NewsletterAPI;