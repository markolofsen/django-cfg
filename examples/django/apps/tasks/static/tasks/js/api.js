/**
 * Tasks API Client
 * Handles all API communication for the Tasks Dashboard
 */
class TasksAPI {
    constructor(baseUrl = '/api/tasks/api') {
        this.baseUrl = baseUrl;
    }

    /**
     * Make API request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} - API response
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);
            
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
     * Get CSRF token from DOM
     * @returns {string} - CSRF token
     */
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // Queue endpoints
    async getQueueStatus() {
        return this.request('/queues/status/');
    }

    // Task endpoints
    async getTaskStatistics() {
        return this.request('/tasks/stats/');
    }

    async getTaskList(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/tasks/list/?${queryString}` : '/tasks/list/';
        return this.request(endpoint);
    }

    // Worker endpoints
    async getWorkersList() {
        return this.request('/workers/list/');
    }

    // Management endpoints
    async simulateData() {
        return this.request('/simulate/', {
            method: 'POST'
        });
    }

    async clearData() {
        return this.request('/clear/', {
            method: 'POST'
        });
    }

    async clearQueues() {
        return this.request('/clear-queues/', {
            method: 'POST'
        });
    }

    async purgeFailed() {
        return this.request('/purge-failed/', {
            method: 'POST'
        });
    }
}

// Export for use in modules
window.TasksAPI = TasksAPI;
window.tasksAPI = new TasksAPI();
