import { BaseAPIClient } from '../base.mjs';

/**
 * Centrifugo API Client
 * Auto-generated from OpenAPI schema
 * @module centrifugo
 * @extends BaseAPIClient
 */
export class CentrifugoAPI extends BaseAPIClient {
    /**
     * Initialize centrifugo API client
     * @param {string} [baseURL] - Optional base URL
     */
    constructor(baseURL) {
        super(baseURL);
    }

    /**
     * Get channel statistics     * Returns statistics grouped by channel.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.hours] - Statistics period in hours (default: 24)     * @returns {Promise<ChannelList>} Response data
     */
    async centrifugoAdminApiMonitorChannelsRetrieve(params = {}) {
        const path = `/cfg/centrifugo/admin/api/monitor/channels/`;        return this.get(path, params);    }
    /**
     * Get Centrifugo health status     * Returns the current health status of the Centrifugo client.     * @returns {Promise<HealthCheck>} Response data
     */
    async centrifugoAdminApiMonitorHealthRetrieve() {
        const path = `/cfg/centrifugo/admin/api/monitor/health/`;        return this.get(path);    }
    /**
     * Get overview statistics     * Returns overview statistics for Centrifugo publishes.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.hours] - Statistics period in hours (default: 24)     * @returns {Promise<OverviewStats>} Response data
     */
    async centrifugoAdminApiMonitorOverviewRetrieve(params = {}) {
        const path = `/cfg/centrifugo/admin/api/monitor/overview/`;        return this.get(path, params);    }
    /**
     * Get recent publishes     * Returns a list of recent Centrifugo publishes with their details.     * @param {Object} [params={}] - Query parameters     * @param {string} [params.channel] - Filter by channel name     * @param {number} [params.count] - Number of publishes to return (default: 50, max: 200)     * @returns {Promise<RecentPublishes>} Response data
     */
    async centrifugoAdminApiMonitorPublishesRetrieve(params = {}) {
        const path = `/cfg/centrifugo/admin/api/monitor/publishes/`;        return this.get(path, params);    }
    /**
     * Get connection token for dashboard     * Returns JWT token and config for WebSocket connection to Centrifugo.     * @returns {Promise<Object>} Response data
     */
    async centrifugoAdminApiServerAuthTokenCreate() {
        const path = `/cfg/centrifugo/admin/api/server/auth/token/`;        return this.post(path, {});    }
    /**
     * List active channels     * Returns list of active channels with optional pattern filter.     * @param {CentrifugoChannelsRequestRequest} data - Request body     * @returns {Promise<CentrifugoChannelsResponse>} Response data
     */
    async centrifugoAdminApiServerChannelsCreate(data) {
        const path = `/cfg/centrifugo/admin/api/server/channels/`;        return this.post(path, data);    }
    /**
     * Get channel history     * Returns message history for a channel.     * @param {CentrifugoHistoryRequestRequest} data - Request body     * @returns {Promise<CentrifugoHistoryResponse>} Response data
     */
    async centrifugoAdminApiServerHistoryCreate(data) {
        const path = `/cfg/centrifugo/admin/api/server/history/`;        return this.post(path, data);    }
    /**
     * Get Centrifugo server info     * Returns server information including node count, version, and uptime.     * @returns {Promise<CentrifugoInfoResponse>} Response data
     */
    async centrifugoAdminApiServerInfoCreate() {
        const path = `/cfg/centrifugo/admin/api/server/info/`;        return this.post(path, {});    }
    /**
     * Get channel presence     * Returns list of clients currently subscribed to a channel.     * @param {CentrifugoPresenceRequestRequest} data - Request body     * @returns {Promise<CentrifugoPresenceResponse>} Response data
     */
    async centrifugoAdminApiServerPresenceCreate(data) {
        const path = `/cfg/centrifugo/admin/api/server/presence/`;        return this.post(path, data);    }
    /**
     * Get channel presence statistics     * Returns quick statistics about channel presence (num_clients, num_users).     * @param {CentrifugoPresenceStatsRequestRequest} data - Request body     * @returns {Promise<CentrifugoPresenceStatsResponse>} Response data
     */
    async centrifugoAdminApiServerPresenceStatsCreate(data) {
        const path = `/cfg/centrifugo/admin/api/server/presence-stats/`;        return this.post(path, data);    }
    /**
     * Generate connection token     * Generate JWT token for WebSocket connection to Centrifugo.     * @param {ConnectionTokenRequestRequest} data - Request body     * @returns {Promise<ConnectionTokenResponse>} Response data
     */
    async centrifugoAdminApiTestingConnectionTokenCreate(data) {
        const path = `/cfg/centrifugo/admin/api/testing/connection-token/`;        return this.post(path, data);    }
    /**
     * Publish test message     * Publish test message to Centrifugo via wrapper with optional ACK tracking.     * @param {PublishTestRequestRequest} data - Request body     * @returns {Promise<PublishTestResponse>} Response data
     */
    async centrifugoAdminApiTestingPublishTestCreate(data) {
        const path = `/cfg/centrifugo/admin/api/testing/publish-test/`;        return this.post(path, data);    }
    /**
     * Publish with database logging     * Publish message using CentrifugoClient with database logging. This will create CentrifugoLog records.     * @param {PublishTestRequestRequest} data - Request body     * @returns {Promise<PublishTestResponse>} Response data
     */
    async centrifugoAdminApiTestingPublishWithLoggingCreate(data) {
        const path = `/cfg/centrifugo/admin/api/testing/publish-with-logging/`;        return this.post(path, data);    }
    /**
     * Send manual ACK     * Manually send ACK for a message to the wrapper. Pass message_id in request body.     * @param {ManualAckRequestRequest} data - Request body     * @returns {Promise<ManualAckResponse>} Response data
     */
    async centrifugoAdminApiTestingSendAckCreate(data) {
        const path = `/cfg/centrifugo/admin/api/testing/send-ack/`;        return this.post(path, data);    }
    /**
     * Get channel statistics     * Returns statistics grouped by channel.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.hours] - Statistics period in hours (default: 24)     * @returns {Promise<ChannelList>} Response data
     */
    async centrifugoMonitorChannelsRetrieve(params = {}) {
        const path = `/cfg/centrifugo/monitor/channels/`;        return this.get(path, params);    }
    /**
     * Get Centrifugo health status     * Returns the current health status of the Centrifugo client.     * @returns {Promise<HealthCheck>} Response data
     */
    async centrifugoMonitorHealthRetrieve() {
        const path = `/cfg/centrifugo/monitor/health/`;        return this.get(path);    }
    /**
     * Get overview statistics     * Returns overview statistics for Centrifugo publishes.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.hours] - Statistics period in hours (default: 24)     * @returns {Promise<OverviewStats>} Response data
     */
    async centrifugoMonitorOverviewRetrieve(params = {}) {
        const path = `/cfg/centrifugo/monitor/overview/`;        return this.get(path, params);    }
    /**
     * Get recent publishes     * Returns a list of recent Centrifugo publishes with their details.     * @param {Object} [params={}] - Query parameters     * @param {string} [params.channel] - Filter by channel name     * @param {number} [params.count] - Number of publishes to return (default: 50, max: 200)     * @returns {Promise<RecentPublishes>} Response data
     */
    async centrifugoMonitorPublishesRetrieve(params = {}) {
        const path = `/cfg/centrifugo/monitor/publishes/`;        return this.get(path, params);    }
    /**
     * Get connection token for dashboard     * Returns JWT token and config for WebSocket connection to Centrifugo.     * @returns {Promise<Object>} Response data
     */
    async centrifugoServerAuthTokenCreate() {
        const path = `/cfg/centrifugo/server/auth/token/`;        return this.post(path, {});    }
    /**
     * List active channels     * Returns list of active channels with optional pattern filter.     * @param {CentrifugoChannelsRequestRequest} data - Request body     * @returns {Promise<CentrifugoChannelsResponse>} Response data
     */
    async centrifugoServerChannelsCreate(data) {
        const path = `/cfg/centrifugo/server/channels/`;        return this.post(path, data);    }
    /**
     * Get channel history     * Returns message history for a channel.     * @param {CentrifugoHistoryRequestRequest} data - Request body     * @returns {Promise<CentrifugoHistoryResponse>} Response data
     */
    async centrifugoServerHistoryCreate(data) {
        const path = `/cfg/centrifugo/server/history/`;        return this.post(path, data);    }
    /**
     * Get Centrifugo server info     * Returns server information including node count, version, and uptime.     * @returns {Promise<CentrifugoInfoResponse>} Response data
     */
    async centrifugoServerInfoCreate() {
        const path = `/cfg/centrifugo/server/info/`;        return this.post(path, {});    }
    /**
     * Get channel presence     * Returns list of clients currently subscribed to a channel.     * @param {CentrifugoPresenceRequestRequest} data - Request body     * @returns {Promise<CentrifugoPresenceResponse>} Response data
     */
    async centrifugoServerPresenceCreate(data) {
        const path = `/cfg/centrifugo/server/presence/`;        return this.post(path, data);    }
    /**
     * Get channel presence statistics     * Returns quick statistics about channel presence (num_clients, num_users).     * @param {CentrifugoPresenceStatsRequestRequest} data - Request body     * @returns {Promise<CentrifugoPresenceStatsResponse>} Response data
     */
    async centrifugoServerPresenceStatsCreate(data) {
        const path = `/cfg/centrifugo/server/presence-stats/`;        return this.post(path, data);    }
    /**
     * Generate connection token     * Generate JWT token for WebSocket connection to Centrifugo.     * @param {ConnectionTokenRequestRequest} data - Request body     * @returns {Promise<ConnectionTokenResponse>} Response data
     */
    async centrifugoTestingConnectionTokenCreate(data) {
        const path = `/cfg/centrifugo/testing/connection-token/`;        return this.post(path, data);    }
    /**
     * Publish test message     * Publish test message to Centrifugo via wrapper with optional ACK tracking.     * @param {PublishTestRequestRequest} data - Request body     * @returns {Promise<PublishTestResponse>} Response data
     */
    async centrifugoTestingPublishTestCreate(data) {
        const path = `/cfg/centrifugo/testing/publish-test/`;        return this.post(path, data);    }
    /**
     * Publish with database logging     * Publish message using CentrifugoClient with database logging. This will create CentrifugoLog records.     * @param {PublishTestRequestRequest} data - Request body     * @returns {Promise<PublishTestResponse>} Response data
     */
    async centrifugoTestingPublishWithLoggingCreate(data) {
        const path = `/cfg/centrifugo/testing/publish-with-logging/`;        return this.post(path, data);    }
    /**
     * Send manual ACK     * Manually send ACK for a message to the wrapper. Pass message_id in request body.     * @param {ManualAckRequestRequest} data - Request body     * @returns {Promise<ManualAckResponse>} Response data
     */
    async centrifugoTestingSendAckCreate(data) {
        const path = `/cfg/centrifugo/testing/send-ack/`;        return this.post(path, data);    }
}

// Default instance for convenience
export const centrifugoAPI = new CentrifugoAPI();

// Default export
export default CentrifugoAPI;