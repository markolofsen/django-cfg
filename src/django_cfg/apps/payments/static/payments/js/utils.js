/**
 * Universal Payment System v2.0 - Utility Functions
 * 
 * Global utilities for the payment system interface.
 */

// Global PaymentSystem namespace
window.PaymentSystem = window.PaymentSystem || {};

/**
 * Utility functions
 */
PaymentSystem.Utils = {
    /**
     * Copy text to clipboard with Material Icons feedback
     * @param {string} text - Text to copy
     * @param {string} successMessage - Success message to show
     */
    copyToClipboard: function(text, successMessage = 'Copied to clipboard!') {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification(successMessage, 'success', 'content_copy');
            }).catch(() => {
                this.fallbackCopyToClipboard(text, successMessage);
            });
        } else {
            this.fallbackCopyToClipboard(text, successMessage);
        }
    },

    /**
     * Fallback copy method for older browsers
     * @param {string} text - Text to copy
     * @param {string} successMessage - Success message to show
     */
    fallbackCopyToClipboard: function(text, successMessage) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showNotification(successMessage, 'success', 'content_copy');
        } catch (err) {
            this.showNotification('Failed to copy to clipboard', 'error', 'error');
        }
        
        document.body.removeChild(textArea);
    },

    /**
     * Show notification with Material Icons
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, warning, info)
     * @param {string} icon - Material icon name
     * @param {number} duration - Duration in milliseconds
     */
    showNotification: function(message, type = 'info', icon = null, duration = 5000) {
        // Remove existing notifications of the same type
        const existingNotifications = document.querySelectorAll(`.notification.${type}`);
        existingNotifications.forEach(notification => {
            notification.remove();
        });

        const notification = document.createElement('div');
        notification.className = `notification ${type} slide-in`;
        
        // Default icons for each type
        const defaultIcons = {
            success: 'check_circle',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };
        
        const iconName = icon || defaultIcons[type] || 'info';
        
        notification.innerHTML = `
            <span class="material-icons-outlined">${iconName}</span>
            <span class="flex-1">${message}</span>
            <button class="close-btn" onclick="this.parentElement.remove()">
                <span class="material-icons-outlined">close</span>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.remove('slide-in');
                notification.classList.add('slide-out');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }
        }, duration);
    },

    /**
     * Format currency with proper locale
     * @param {number} amount - Amount to format
     * @param {string} currency - Currency code
     * @param {string} locale - Locale for formatting
     * @returns {string} Formatted currency string
     */
    formatCurrency: function(amount, currency = 'USD', locale = 'en-US') {
        try {
            return new Intl.NumberFormat(locale, {
                style: 'currency',
                currency: currency,
                minimumFractionDigits: currency === 'USD' ? 2 : 8
            }).format(amount);
        } catch (error) {
            return `${amount} ${currency}`;
        }
    },

    /**
     * Format date with relative time
     * @param {string|Date} dateString - Date to format
     * @param {boolean} relative - Whether to show relative time
     * @returns {string} Formatted date string
     */
    formatDate: function(dateString, relative = false) {
        const date = new Date(dateString);
        
        if (relative) {
            const now = new Date();
            const diffInSeconds = Math.floor((now - date) / 1000);
            
            if (diffInSeconds < 60) return 'Just now';
            if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
            if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
            if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
        }
        
        return date.toLocaleString();
    },

    /**
     * Debounce function calls
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @param {boolean} immediate - Whether to execute immediately
     * @returns {Function} Debounced function
     */
    debounce: function(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(this, args);
        };
    },

    /**
     * Throttle function calls
     * @param {Function} func - Function to throttle
     * @param {number} limit - Time limit in milliseconds
     * @returns {Function} Throttled function
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Generate random ID
     * @param {number} length - Length of ID
     * @returns {string} Random ID
     */
    generateId: function(length = 8) {
        return Math.random().toString(36).substring(2, length + 2);
    },

    /**
     * Validate email address
     * @param {string} email - Email to validate
     * @returns {boolean} Whether email is valid
     */
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    /**
     * Validate URL
     * @param {string} url - URL to validate
     * @returns {boolean} Whether URL is valid
     */
    isValidUrl: function(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },

    /**
     * Get status badge class
     * @param {string} status - Status value
     * @returns {string} CSS class for status badge
     */
    getStatusBadgeClass: function(status) {
        const statusMap = {
            'completed': 'success',
            'success': 'success',
            'active': 'success',
            'failed': 'error',
            'error': 'error',
            'cancelled': 'error',
            'pending': 'warning',
            'processing': 'info',
            'inactive': 'error'
        };
        
        return `status-badge ${statusMap[status.toLowerCase()] || 'info'}`;
    },

    /**
     * Get Material Icon for status
     * @param {string} status - Status value
     * @returns {string} Material icon name
     */
    getStatusIcon: function(status) {
        const iconMap = {
            'completed': 'check_circle',
            'success': 'check_circle',
            'active': 'check_circle',
            'failed': 'error',
            'error': 'error',
            'cancelled': 'cancel',
            'pending': 'schedule',
            'processing': 'sync',
            'inactive': 'radio_button_unchecked'
        };
        
        return iconMap[status.toLowerCase()] || 'help';
    },

    /**
     * Format file size
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted file size
     */
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Scroll to element smoothly
     * @param {string|Element} element - Element or selector
     * @param {number} offset - Offset from top
     */
    scrollToElement: function(element, offset = 0) {
        const target = typeof element === 'string' ? document.querySelector(element) : element;
        if (target) {
            const targetPosition = target.offsetTop - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    },

    /**
     * Check if element is in viewport
     * @param {Element} element - Element to check
     * @returns {boolean} Whether element is in viewport
     */
    isInViewport: function(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

/**
 * Auto-refresh functionality
 */
PaymentSystem.AutoRefresh = {
    interval: null,
    
    /**
     * Setup auto-refresh for elements with data-auto-refresh attribute
     * @param {number} intervalMs - Refresh interval in milliseconds
     */
    setup: function(intervalMs = 30000) {
        if (document.querySelector('[data-auto-refresh]')) {
            this.interval = setInterval(() => {
                this.refresh();
            }, intervalMs);
        }
    },
    
    /**
     * Refresh the page or specific elements
     */
    refresh: function() {
        const elements = document.querySelectorAll('[data-auto-refresh]');
        if (elements.length > 0) {
            elements.forEach(element => {
                const refreshType = element.getAttribute('data-auto-refresh');
                if (refreshType === 'page') {
                    location.reload();
                } else if (refreshType === 'ajax' && element.hasAttribute('data-refresh-url')) {
                    this.refreshElement(element);
                }
            });
        }
    },
    
    /**
     * Refresh specific element via AJAX
     * @param {Element} element - Element to refresh
     */
    refreshElement: function(element) {
        const url = element.getAttribute('data-refresh-url');
        if (url) {
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    element.innerHTML = html;
                })
                .catch(error => {
                    console.error('Auto-refresh failed:', error);
                });
        }
    },
    
    /**
     * Stop auto-refresh
     */
    stop: function() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }
};

/**
 * Initialize utilities on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Setup auto-refresh if enabled
    PaymentSystem.AutoRefresh.setup();
    
    // Add global keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search (if search exists)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            const searchInput = document.querySelector('[data-search]');
            if (searchInput) {
                e.preventDefault();
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal-overlay');
            modals.forEach(modal => {
                if (modal.style.display !== 'none') {
                    modal.style.display = 'none';
                }
            });
        }
    });
    
    // Add click-to-copy functionality for elements with data-copy attribute
    document.addEventListener('click', function(e) {
        const copyElement = e.target.closest('[data-copy]');
        if (copyElement) {
            const textToCopy = copyElement.getAttribute('data-copy') || copyElement.textContent;
            PaymentSystem.Utils.copyToClipboard(textToCopy);
        }
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PaymentSystem;
}
