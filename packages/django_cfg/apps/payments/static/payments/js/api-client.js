/**
 * Payment API Client
 * Provides convenient methods for API calls with automatic JSON handling
 */
class PaymentAPIClient {
    constructor() {
        this.baseURL = '/api/payments';
        this.adminURL = '/cfg/admin/django_cfg_payments/admin';
    }

    // Helper method to get CSRF token
    getCSRFToken() {
        // Try to get token from form input first
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenInput && tokenInput.value) {
            return tokenInput.value;
        }
        
        // Fallback to cookie
        const cookieString = document.cookie;
        if (cookieString.includes('csrftoken=')) {
            const match = cookieString.match(/csrftoken=([^;]+)/);
            if (match) {
                return match[1];
            }
        }
            
        return '';
    }

    // Generic request method
    async request(url, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ message: 'Request failed' }));
                throw new Error(error.message || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // GET request
    async get(url, params = {}) {
        const urlWithParams = new URL(url, window.location.origin);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                urlWithParams.searchParams.append(key, value);
            }
        });
        
        return this.request(urlWithParams.toString());
    }

    // POST request
    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }

    // PAYMENTS API
    payments = {
        // Get all payments
        list: (params = {}) => this.get(`${this.baseURL}/payments/`, params),
        
        // Get payment by ID
        get: (id) => this.get(`${this.baseURL}/payments/${id}/`),
        
        // Create payment
        create: (data) => this.post(`${this.baseURL}/payments/create/`, data),
        
        // Get payment status
        status: (id) => this.get(`${this.baseURL}/payments/status/${id}/`),
        
        // Check payment status
        checkStatus: (id) => this.post(`${this.baseURL}/payments/${id}/check_status/`),
        
        // Cancel payment
        cancel: (id) => this.post(`${this.baseURL}/payments/${id}/cancel/`),
        
        // Get payment stats
        stats: () => this.get(`${this.baseURL}/payments/stats/`),
        
        // Get payment analytics
        analytics: (params = {}) => this.get(`${this.baseURL}/payments/analytics/`, params),
        
        // Get payments by provider
        byProvider: (provider) => this.get(`${this.baseURL}/payments/by_provider/`, { provider })
    };

    // WEBHOOKS API
    webhooks = {
        // Get webhook stats
        stats: () => this.get(`${this.baseURL}/webhooks/stats/`),
        
        // Get supported providers
        providers: () => this.get(`${this.baseURL}/webhooks/providers/`),
        
        // Health check
        health: () => this.get(`${this.baseURL}/webhooks/health/`)
    };

    // CURRENCIES API
    currencies = {
        // Get all currencies
        list: () => this.get(`${this.baseURL}/currencies/`),
        
        // Get currency by ID
        get: (id) => this.get(`${this.baseURL}/currencies/${id}/`),
        
        // Get supported currencies
        supported: (params = {}) => this.get(`${this.baseURL}/currencies/supported/`, params),
        
        // Get currencies by provider
        byProvider: (provider) => this.get(`${this.baseURL}/provider-currencies/`, { provider, page_size: 1000 }),
        
        // Get exchange rates
        rates: (params = {}) => this.get(`${this.baseURL}/currencies/rates/`, params),
        
        // Convert currency
        convert: (from, to, amount) => this.post(`${this.baseURL}/currencies/convert/`, { 
            from_currency: from, 
            to_currency: to, 
            amount: amount 
        }),
        
        // Get provider-specific currency configurations
        providerConfigs: (provider) => this.get(`${this.baseURL}/provider-currencies/`, { provider, page_size: 1000 }),
        
        // Get currencies grouped by provider
        byProviderGrouped: () => this.get(`${this.baseURL}/provider-currencies/by_provider/`)
    };

    // BALANCES API
    balances = {
        // Get all balances
        list: (params = {}) => this.get(`${this.baseURL}/balances/`, params),
        
        // Get balance by ID
        get: (id) => this.get(`${this.baseURL}/balances/${id}/`),
        
        // Top up balance
        topup: (id, amount, currency) => this.post(`${this.baseURL}/balances/${id}/topup/`, { amount, currency }),
        
        // Withdraw from balance
        withdraw: (id, amount, currency) => this.post(`${this.baseURL}/balances/${id}/withdraw/`, { amount, currency })
    };

    // TRANSACTIONS API
    transactions = {
        // Get all transactions
        list: (params = {}) => this.get(`${this.baseURL}/transactions/`, params),
        
        // Get transaction by ID
        get: (id) => this.get(`${this.baseURL}/transactions/${id}/`),
        
        // Get recent transactions
        recent: (limit = 10) => this.get(`${this.baseURL}/transactions/recent/`, { limit }),
        
        // Get transactions by type
        byType: (type) => this.get(`${this.baseURL}/transactions/by_type/`, { type }),
        
        // Get transaction stats
        stats: () => this.get(`${this.baseURL}/transactions/stats/`)
    };

    // API KEYS API
    apiKeys = {
        // Get all API keys
        list: () => this.get(`${this.baseURL}/api-keys/`),
        
        // Get API key by ID
        get: (id) => this.get(`${this.baseURL}/api-keys/${id}/`),
        
        // Generate new API key
        generate: (data) => this.post(`${this.baseURL}/api-keys/generate/`, data),
        
        // Revoke API key
        revoke: (id) => this.post(`${this.baseURL}/api-keys/${id}/revoke/`),
        
        // Get API key stats
        stats: () => this.get(`${this.baseURL}/api-keys/stats/`)
    };

    // DASHBOARD API
    dashboard = {
        // Get dashboard overview
        overview: () => this.get(`${this.baseURL}/overview/dashboard/overview/`),
        
        // Get dashboard metrics
        metrics: () => this.get(`${this.baseURL}/overview/dashboard/metrics/`),
        
        // Get chart data
        chartData: (period = '7d') => this.get(`${this.baseURL}/overview/dashboard/chart_data/`, { period }),
        
        // Get recent payments
        recentPayments: (limit = 5) => this.get(`${this.baseURL}/overview/dashboard/recent_payments/`, { limit }),
        
        // Get recent transactions
        recentTransactions: (limit = 5) => this.get(`${this.baseURL}/overview/dashboard/recent_transactions/`, { limit }),
        
        // Get payment analytics
        paymentAnalytics: () => this.get(`${this.baseURL}/overview/dashboard/payment_analytics/`),
        
        // Get balance overview
        balanceOverview: () => this.get(`${this.baseURL}/overview/dashboard/balance_overview/`),
        
        // Get subscription overview
        subscriptionOverview: () => this.get(`${this.baseURL}/overview/dashboard/subscription_overview/`),
        
        // Get API keys overview
        apiKeysOverview: () => this.get(`${this.baseURL}/overview/dashboard/api_keys_overview/`)
    };

    // NGROK API (custom endpoints)
    ngrok = {
        // Get ngrok status from webhook health endpoint
        status: async () => {
            try {
                const response = await this.get('/api/payments/webhooks/health/');
                const ngrokActive = response.details?.ngrok_available || false;
                const apiUrl = response.details?.api_base_url || '';
                
                if (ngrokActive) {
                    return {
                        active: true,
                        public_url: apiUrl,
                        webhook_url: apiUrl + '/api/payments/webhooks/',
                        region: 'auto',
                        proto: apiUrl.startsWith('https') ? 'https' : 'http',
                        error: null
                    };
                } else {
                    return {
                        active: false,
                        public_url: '',
                        webhook_url: '',
                        region: 'us',
                        proto: 'https',
                        error: 'Ngrok tunnel not active'
                    };
                }
            } catch (error) {
                return {
                    active: false,
                    public_url: '',
                    webhook_url: '',
                    region: 'us',
                    proto: 'https',
                    error: error.message || 'Health check API not accessible'
                };
            }
        },
        
        // Start ngrok tunnel (placeholder - not implemented)
        start: () => this.post(`${this.adminURL}/ngrok/start/`),
        
        // Stop ngrok tunnel (placeholder - not implemented)
        stop: () => this.post(`${this.adminURL}/ngrok/stop/`)
    };

    // ADMIN API ENDPOINTS (DRF nested router structure)
    admin = {
        // Payments API
        payments: {
            list: (params = {}) => this.get(`${this.adminURL}/api/payments/`, params),
            get: (id) => this.get(`${this.adminURL}/api/payments/${id}/`),
            create: (data) => this.post(`${this.adminURL}/api/payments/`, data),
            update: (id, data) => this.patch(`${this.adminURL}/api/payments/${id}/`, data),
            delete: (id) => this.delete(`${this.adminURL}/api/payments/${id}/`),
            cancel: (id) => this.post(`${this.adminURL}/api/payments/${id}/cancel/`),
            refund: (id) => this.post(`${this.adminURL}/api/payments/${id}/refund/`),
            refreshStatus: (id) => this.post(`${this.adminURL}/api/payments/${id}/refresh_status/`),
            stats: () => this.get(`${this.adminURL}/api/payments/stats/`)
        },
        
        // Webhooks API
        webhooks: {
            list: () => this.get(`${this.adminURL}/api/webhooks/`),
            stats: () => this.get(`${this.adminURL}/api/webhooks/stats/`),
            
            // Nested webhook events
            events: {
                list: (webhookId = 1, params = {}) => this.get(`${this.adminURL}/api/webhooks/${webhookId}/events/`, params),
                retry: (webhookId, eventId) => this.post(`${this.adminURL}/api/webhooks/${webhookId}/events/${eventId}/retry/`),
                clearAll: (webhookId) => this.post(`${this.adminURL}/api/webhooks/${webhookId}/events/clear_all/`),
                retryFailed: (webhookId) => this.post(`${this.adminURL}/api/webhooks/${webhookId}/events/retry_failed/`)
            }
        },
        
        // Webhook test method
        webhookTest: {
            send: (url, eventType) => this.post(`${this.adminURL}/api/webhook-test/test/`, { 
                webhook_url: url, 
                event_type: eventType 
            })
        },
        
        // Stats API
        stats: {
            overview: () => this.get(`${this.adminURL}/api/stats/`),
            payments: () => this.get(`${this.adminURL}/api/stats/payments/`),
            webhooks: () => this.get(`${this.adminURL}/api/stats/webhooks/`),
            system: () => this.get(`${this.adminURL}/api/stats/system/`)
        },
        
        // Users API
        users: {
            list: (params = {}) => this.get(`${this.adminURL}/api/users/`, params),
            get: (id) => this.get(`${this.adminURL}/api/users/${id}/`),
            search: (query) => this.get(`${this.adminURL}/api/users/`, { q: query })
        }
    };


    // Utility methods
    utils = {
        // Format currency
        formatCurrency: (amount, currency = 'USD') => {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: currency
            }).format(amount);
        },

        // Format date
        formatDate: (dateString) => {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        // Show notification (simple implementation)
        showNotification: (message, type = 'info') => {
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 px-4 py-2 rounded-md shadow-lg z-50 ${
                type === 'success' ? 'bg-green-500 text-white' :
                type === 'error' ? 'bg-red-500 text-white' :
                type === 'warning' ? 'bg-yellow-500 text-white' :
                'bg-blue-500 text-white'
            }`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        },

        // Copy to clipboard
        copyToClipboard: async (text) => {
            try {
                await navigator.clipboard.writeText(text);
                PaymentAPI.utils.showNotification('Copied to clipboard!', 'success');
            } catch (error) {
                console.error('Failed to copy:', error);
                PaymentAPI.utils.showNotification('Failed to copy', 'error');
            }
        }
    };
}

// Create global instance
console.log('🔧 PaymentAPIClient: Creating global instance...');
window.PaymentAPI = new PaymentAPIClient();
console.log('✅ PaymentAPIClient: Global instance created');
console.log('🔍 PaymentAPI.currencies:', window.PaymentAPI.currencies);
console.log('🔍 PaymentAPI.admin:', window.PaymentAPI.admin);

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PaymentAPIClient;
}
