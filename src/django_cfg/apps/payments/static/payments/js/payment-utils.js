/**
 * Payment Utility Functions
 * Common utilities for payment dashboard functionality
 */

class PaymentUtils {
    constructor() {
        this.formatters = {
            currency: new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 8
            }),
            number: new Intl.NumberFormat('en-US'),
            date: new Intl.DateTimeFormat('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            })
        };
    }

    // Format currency with proper decimals based on currency type
    formatCurrency(amount, currencyCode = 'USD') {
        const numAmount = parseFloat(amount) || 0;
        
        // Crypto currencies need more decimal places
        const cryptoDecimals = {
            'BTC': 8,
            'ETH': 6,
            'LTC': 8,
            'USDT': 6,
            'USDC': 6
        };

        if (cryptoDecimals[currencyCode]) {
            return `${numAmount.toFixed(cryptoDecimals[currencyCode])} ${currencyCode}`;
        }

        // Fiat currencies
        if (currencyCode === 'USD') {
            return this.formatters.currency.format(numAmount);
        }

        return `${numAmount.toFixed(2)} ${currencyCode}`;
    }

    // Format payment status with proper display text
    formatStatus(status) {
        const statusMap = {
            'pending': 'Pending',
            'confirming': 'Confirming',
            'confirmed': 'Confirmed',
            'completed': 'Completed',
            'failed': 'Failed',
            'expired': 'Expired',
            'cancelled': 'Cancelled',
            'refunded': 'Refunded'
        };
        return statusMap[status] || status;
    }

    // Get status color class
    getStatusColor(status) {
        const colorMap = {
            'pending': 'yellow',
            'confirming': 'blue',
            'confirmed': 'green',
            'completed': 'green',
            'failed': 'red',
            'expired': 'gray',
            'cancelled': 'gray',
            'refunded': 'purple'
        };
        return colorMap[status] || 'gray';
    }

    // Get provider display name
    getProviderName(provider) {
        const providerMap = {
            'nowpayments': 'NowPayments',
            'cryptapi': 'CryptAPI',
            'cryptomus': 'Cryptomus',
            'stripe': 'Stripe',
            'internal': 'Internal'
        };
        return providerMap[provider] || provider;
    }

    // Get provider icon
    getProviderIcon(provider) {
        const iconMap = {
            'nowpayments': 'currency_bitcoin',
            'cryptapi': 'currency_bitcoin',
            'cryptomus': 'currency_bitcoin',
            'stripe': 'credit_card',
            'internal': 'account_balance'
        };
        return iconMap[provider] || 'payment';
    }

    // Calculate time ago
    timeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffSecs < 60) {
            return 'Just now';
        } else if (diffMins < 60) {
            return `${diffMins}m ago`;
        } else if (diffHours < 24) {
            return `${diffHours}h ago`;
        } else if (diffDays < 7) {
            return `${diffDays}d ago`;
        } else {
            return this.formatters.date.format(date);
        }
    }

    // Validate payment ID format
    isValidPaymentId(id) {
        // UUID v4 format
        const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
        return uuidRegex.test(id);
    }

    // Copy text to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            if (window.notificationManager) {
                window.notificationManager.success('Copied to clipboard');
            }
            return true;
        } catch (err) {
            console.error('Failed to copy to clipboard:', err);
            if (window.notificationManager) {
                window.notificationManager.error('Failed to copy to clipboard');
            }
            return false;
        }
    }

    // Generate QR code data URL (placeholder - requires QR library)
    generateQRCodeDataUrl(data, size = 128) {
        // This would integrate with a QR code library like qrcode.js
        // For now, return a placeholder
        return `data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"><rect width="100%" height="100%" fill="%23f3f4f6"/><text x="50%" y="50%" text-anchor="middle" dy="0.3em" font-family="sans-serif" font-size="12" fill="%236b7280">QR Code</text></svg>`;
    }

    // Debounce function for search/filter inputs
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Throttle function for scroll events
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Update URL parameters without page reload
    updateUrlParams(params) {
        const url = new URL(window.location);
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== '') {
                url.searchParams.set(key, params[key]);
            } else {
                url.searchParams.delete(key);
            }
        });
        window.history.replaceState({}, '', url);
    }

    // Get URL parameter value
    getUrlParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    // Format large numbers (e.g., 1000000 -> 1M)
    formatLargeNumber(num) {
        const numValue = parseFloat(num) || 0;
        if (numValue >= 1000000000) {
            return (numValue / 1000000000).toFixed(1) + 'B';
        } else if (numValue >= 1000000) {
            return (numValue / 1000000).toFixed(1) + 'M';
        } else if (numValue >= 1000) {
            return (numValue / 1000).toFixed(1) + 'K';
        }
        return this.formatters.number.format(numValue);
    }

    // Show confirmation dialog
    showConfirmDialog(message, onConfirm, onCancel = null) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white">Confirm Action</h3>
                </div>
                <div class="modal-body">
                    <p class="text-sm text-gray-500 dark:text-gray-400">${this.escapeHtml(message)}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" id="cancel-btn">Cancel</button>
                    <button class="btn btn-danger" id="confirm-btn">Confirm</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const confirmBtn = modal.querySelector('#confirm-btn');
        const cancelBtn = modal.querySelector('#cancel-btn');

        const cleanup = () => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        };

        confirmBtn.addEventListener('click', () => {
            cleanup();
            if (onConfirm) onConfirm();
        });

        cancelBtn.addEventListener('click', () => {
            cleanup();
            if (onCancel) onCancel();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                cleanup();
                if (onCancel) onCancel();
            }
        });
    }

    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }

    // Local storage helpers with error handling
    setStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Failed to save to localStorage:', e);
            return false;
        }
    }

    getStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Failed to read from localStorage:', e);
            return defaultValue;
        }
    }

    removeStorage(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('Failed to remove from localStorage:', e);
            return false;
        }
    }
}

// Initialize utils when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.paymentUtils = new PaymentUtils();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PaymentUtils;
}
