/**
 * Django CFG Utility Functions
 *
 * Modern ES6+ utility functions for the admin interface
 * These are minimal utilities that don't require Alpine.js
 */

/**
 * Get CSRF token from cookies
 * @param {string} name - Cookie name (usually 'csrftoken')
 * @returns {string|null} Cookie value or null if not found
 */
function getCookie(name) {
    if (!document.cookie) return null;

    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split('=');
        if (cookieName === name) {
            return decodeURIComponent(cookieValue);
        }
    }
    return null;
}

/**
 * Copy text to clipboard with visual feedback
 * @param {Event} event - Click event from button
 * @param {string} text - Text to copy
 */
async function copyToClipboard(event, text) {
    try {
        await navigator.clipboard.writeText(text);

        const button = event?.target?.closest('button');
        if (!button) return;

        // Store original state
        const originalHTML = button.innerHTML;
        const originalClasses = button.className;

        // Show success state
        button.innerHTML = '<span class="material-icons text-xs mr-1">check</span>Copied';
        button.className = 'inline-flex items-center justify-center px-3 py-2 bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 text-white rounded-lg text-xs font-medium transition-colors';

        // Reset after 2 seconds
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.className = originalClasses;
        }, 2000);
    } catch (err) {
        console.error('Failed to copy to clipboard:', err);
    }
}

// Export to window for global access
if (typeof window !== 'undefined') {
    window.getCookie = getCookie;
    window.copyToClipboard = copyToClipboard;
}
