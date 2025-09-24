/**
 * API Client for Dramatiq Tasks Dashboard
 * Handles all API communication with the backend
 */

class TasksAPI {
    constructor(baseUrl = '/cfg/tasks/api') {
        this.baseUrl = baseUrl;
    }

    /**
     * Make an API request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} API response
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin', // Include cookies for session authentication
        };

        // Add CSRF token if available
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfToken) {
            // Try alternative selectors
            csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        }
        if (!csrfToken) {
            // Try getting from cookie
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {
                    defaultOptions.headers['X-CSRFToken'] = value;
                    break;
                }
            }
        } else {
            defaultOptions.headers['X-CSRFToken'] = csrfToken.value;
        }

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Get queue status
     * @returns {Promise<Object>} Queue status data
     */
    async getQueueStatus() {
        return this.request('/queues/status/');
    }

    /**
     * Get task statistics
     * @returns {Promise<Object>} Task statistics data
     */
    async getTaskStatistics() {
        return this.request('/tasks/stats/');
    }

    /**
     * Get detailed task list
     * @param {Object} params - Query parameters (status, queue, search, limit, offset)
     * @returns {Promise<Object>} Task list
     */
    async getTaskList(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = `/tasks/list/${queryString ? '?' + queryString : ''}`;
        return this.request(url);
    }

    /**
     * Start workers
     * @param {Object} config - Worker configuration
     * @returns {Promise<Object>} Operation result
     */
    async startWorkers(config = {}) {
        return this.request('/workers/manage/', {
            method: 'POST',
            body: JSON.stringify({
                action: 'start',
                ...config
            })
        });
    }

    /**
     * Stop workers
     * @returns {Promise<Object>} Operation result
     */
    async stopWorkers() {
        return this.request('/workers/manage/', {
            method: 'POST',
            body: JSON.stringify({
                action: 'stop'
            })
        });
    }

    /**
     * Clear all queues
     * @returns {Promise<Object>} Operation result
     */
    async clearQueues() {
        return this.request('/queues/manage/', {
            method: 'POST',
            body: JSON.stringify({
                action: 'clear_all'
            })
        });
    }

    /**
     * Purge failed tasks
     * @returns {Promise<Object>} Operation result
     */
    async purgeFailedTasks() {
        return this.request('/queues/manage/', {
            method: 'POST',
            body: JSON.stringify({
                action: 'purge_failed'
            })
        });
    }
}

// Create global API instance
window.tasksAPI = new TasksAPI();
