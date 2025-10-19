/**
 * Base API Client for django-cfg
 * Lightweight ES Module with JSDoc type annotations
 * @module base
 */

/**
 * Custom error class for API errors
 * @class APIError
 * @extends Error
 */
class APIError extends Error {
    /**
     * @param {string} message - Error message
     * @param {number} status - HTTP status code
     * @param {any} data - Additional error data
     */
    constructor(message, status, data) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

/**
 * Get Django CSRF token from cookies
 * @returns {string} CSRF token value
 */
function getCsrfToken() {
    const cookie = document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

/**
 * @typedef {Object} RequestOptions
 * @property {string} [method='GET'] - HTTP method
 * @property {Object} [headers={}] - Request headers
 * @property {any} [body] - Request body
 * @property {string} [credentials='same-origin'] - Credentials mode
 */

/**
 * Base API client class with built-in Django CSRF support
 * @class BaseAPIClient
 */
export class BaseAPIClient {
    /**
     * Initialize the API client
     * @param {string} [baseURL=''] - Base URL for API requests (defaults to current origin)
     */
    constructor(baseURL = '') {
        this.baseURL = baseURL || window.location.origin;
    }

    /**
     * Make an API request
     * @param {string} path - API endpoint path
     * @param {RequestOptions} [options={}] - Request options
     * @returns {Promise<any>} Response data
     * @throws {APIError} When request fails
     */
    async request(path, options = {}) {
        const url = `${this.baseURL}${path}`;

        // Default headers with CSRF token
        const headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                credentials: 'same-origin'
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new APIError(
                    error.detail || `HTTP ${response.status}`,
                    response.status,
                    error
                );
            }

            // Handle empty responses
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError(error.message, 0, null);
        }
    }

    /**
     * Make a GET request
     * @param {string} path - API endpoint path
     * @param {Object} [params={}] - Query parameters
     * @returns {Promise<any>} Response data
     */
    async get(path, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullPath = queryString ? `${path}?${queryString}` : path;
        return this.request(fullPath, { method: 'GET' });
    }

    /**
     * Make a POST request
     * @param {string} path - API endpoint path
     * @param {any} [data={}] - Request body data
     * @returns {Promise<any>} Response data
     */
    async post(path, data = {}) {
        return this.request(path, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * Make a PUT request
     * @param {string} path - API endpoint path
     * @param {any} [data={}] - Request body data
     * @returns {Promise<any>} Response data
     */
    async put(path, data = {}) {
        return this.request(path, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * Make a PATCH request
     * @param {string} path - API endpoint path
     * @param {any} [data={}] - Request body data
     * @returns {Promise<any>} Response data
     */
    async patch(path, data = {}) {
        return this.request(path, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    /**
     * Make a DELETE request
     * @param {string} path - API endpoint path
     * @returns {Promise<any>} Response data
     */
    async delete(path) {
        return this.request(path, { method: 'DELETE' });
    }
}

// Export the error class as well
export { APIError };