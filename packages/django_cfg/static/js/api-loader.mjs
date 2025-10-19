/**
 * API Loader Module
 * Provides centralized loading of MJS API clients with error handling
 * @module api-loader
 */

/**
 * Load and initialize an API module
 * @param {string} appName - Name of the app (e.g., 'tasks', 'payments')
 * @returns {Promise<Object>} The API instance
 */
export async function loadAPI(appName) {
    try {
        const module = await import(`/static/js/api/${appName}/index.mjs`);
        const apiName = `${appName}API`;
        const instanceName = `${appName.charAt(0).toLowerCase() + appName.slice(1)}API`;

        // Return the default instance
        return module[instanceName] || module.default;
    } catch (error) {
        console.error(`Failed to load ${appName} API:`, error);
        throw new Error(`API module '${appName}' could not be loaded`);
    }
}

/**
 * Load multiple API modules
 * @param {string[]} appNames - Array of app names
 * @returns {Promise<Object>} Object with loaded APIs
 */
export async function loadAPIs(appNames) {
    const apis = {};

    for (const appName of appNames) {
        try {
            apis[appName] = await loadAPI(appName);
            console.log(`✅ Loaded ${appName} API with JSDoc types`);
        } catch (error) {
            console.error(`❌ Failed to load ${appName} API:`, error);
            apis[appName] = null;
        }
    }

    return apis;
}

/**
 * Create an API wrapper with error handling
 * @param {Object} api - The API instance
 * @returns {Proxy} Proxied API with automatic error handling
 */
export function wrapAPI(api) {
    return new Proxy(api, {
        get(target, prop) {
            const original = target[prop];

            if (typeof original === 'function') {
                return async function(...args) {
                    try {
                        console.log(`🔵 API Call: ${prop}`, args);
                        const result = await original.apply(target, args);
                        console.log(`✅ API Response:`, result);
                        return result;
                    } catch (error) {
                        console.error(`❌ API Error in ${prop}:`, error);

                        // Extract meaningful error message
                        let message = 'An error occurred';
                        if (error.data?.detail) {
                            message = error.data.detail;
                        } else if (error.message) {
                            message = error.message;
                        }

                        // Show notification if available
                        if (window.showNotification) {
                            window.showNotification(message, 'error');
                        }

                        throw error;
                    }
                };
            }

            return original;
        }
    });
}

/**
 * Initialize APIs and make them globally available
 * @param {string[]} appNames - Array of app names to load
 * @returns {Promise<Object>} Object with loaded and wrapped APIs
 */
export async function initializeAPIs(appNames) {
    const apis = await loadAPIs(appNames);
    const wrappedAPIs = {};

    for (const [name, api] of Object.entries(apis)) {
        if (api) {
            wrappedAPIs[name] = wrapAPI(api);
            // Make available globally for non-module scripts
            window[`${name}API`] = wrappedAPIs[name];
        }
    }

    return wrappedAPIs;
}

/**
 * Utility function to show notifications
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, info)
 * @param {number} duration - Duration in milliseconds
 */
export function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');

    // Style based on type
    const styles = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-white',
        info: 'bg-blue-500 text-white'
    };

    notification.className = `
        fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50
        transform transition-all duration-300 ease-in-out
        ${styles[type] || styles.info}
    `;

    notification.innerHTML = `
        <div class="flex items-center">
            <span class="material-icons mr-2">
                ${type === 'success' ? 'check_circle' :
                  type === 'error' ? 'error' :
                  type === 'warning' ? 'warning' :
                  'info'}
            </span>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);

    // Remove after duration
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Make notification function globally available
window.showNotification = showNotification;

// Export everything for use in modules
export default {
    loadAPI,
    loadAPIs,
    wrapAPI,
    initializeAPIs,
    showNotification
};