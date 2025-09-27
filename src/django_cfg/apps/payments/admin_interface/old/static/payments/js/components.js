/**
 * Universal Payment System v2.0 - Component Functions
 * 
 * Reusable Alpine.js components and interactive functionality.
 */

// Ensure PaymentSystem namespace exists
window.PaymentSystem = window.PaymentSystem || {};

/**
 * Alpine.js Components
 */
PaymentSystem.Components = {
    /**
     * Webhook Dashboard Component
     */
    webhookDashboard: function() {
        return {
            loading: true,
            providers: [],
            ngrokStatus: {
                active: false,
                url: null,
                description: 'Checking...'
            },
            healthStatus: {
                healthy: false,
                description: 'Checking...',
                last_check: null
            },
            stats: {
                total_webhooks: 0,
                successful_webhooks: 0,
                failed_webhooks: 0,
                recent_count: 0,
                recent_activity: []
            },
            showTestModal: false,
            testProvider: '',
            testData: '{"payment_id": "test_123", "status": "completed", "amount": "10.00"}',
            testLoading: false,
            lastTest: null,
            testStatus: null,

            async init() {
                await this.loadData();
            },

            async loadData() {
                this.loading = true;
                try {
                    await Promise.all([
                        this.loadProviders(),
                        this.checkHealth(),
                        this.loadStats()
                    ]);
                } catch (error) {
                    console.error('Failed to load dashboard data:', error);
                    PaymentSystem.Utils.showNotification('Failed to load dashboard data', 'error');
                } finally {
                    this.loading = false;
                }
            },

            async loadProviders() {
                try {
                    const response = await fetch('/api/payments/webhooks/providers/');
                    const data = await response.json();
                    
                    if (data.success) {
                        this.providers = data.providers || [];
                    } else {
                        throw new Error(data.error || 'Failed to load providers');
                    }
                } catch (error) {
                    console.error('Failed to load providers:', error);
                    this.providers = [];
                }
            },

            async checkHealth() {
                try {
                    const response = await fetch('/api/payments/webhooks/health/');
                    const data = await response.json();
                    
                    this.healthStatus = {
                        healthy: data.status === 'healthy',
                        description: data.status === 'healthy' ? 'Service healthy' : (data.error || 'Unknown status'),
                        last_check: new Date().toLocaleString()
                    };

                    // Update ngrok status from details
                    const ngrokAvailable = data.details?.ngrok_available || false;
                    this.ngrokStatus = {
                        active: ngrokAvailable,
                        url: data.details?.api_base_url || null,
                        description: ngrokAvailable ? 'Tunnel active' : 'Tunnel inactive'
                    };
                } catch (error) {
                    console.error('Failed to check health:', error);
                    this.healthStatus = {
                        healthy: false,
                        description: 'Health check failed',
                        last_check: new Date().toLocaleString()
                    };
                }
            },

            async loadStats() {
                try {
                    const response = await fetch('/api/payments/webhooks/stats/');
                    const data = await response.json();
                    
                    if (data.success) {
                        this.stats = {
                            total_webhooks: data.stats.total_webhooks || 0,
                            successful_webhooks: data.stats.successful_webhooks || 0,
                            failed_webhooks: data.stats.failed_webhooks || 0,
                            recent_count: data.stats.recent_count || 0,
                            recent_activity: data.stats.recent_activity || []
                        };
                    }
                } catch (error) {
                    console.error('Failed to load stats:', error);
                    this.stats = {
                        total_webhooks: 0,
                        successful_webhooks: 0,
                        failed_webhooks: 0,
                        recent_count: 0,
                        recent_activity: []
                    };
                }
            },

            async refreshData() {
                await this.loadData();
                PaymentSystem.Utils.showNotification('Dashboard data refreshed', 'success', 'refresh');
            },

            async checkNgrokStatus() {
                await this.checkHealth();
                PaymentSystem.Utils.showNotification('Ngrok status updated', 'info', 'network_check');
            },

            async sendTestWebhook() {
                if (!this.testProvider) {
                    PaymentSystem.Utils.showNotification('Please select a provider', 'warning', 'warning');
                    return;
                }

                this.testLoading = true;
                try {
                    const provider = this.providers.find(p => p.name === this.testProvider);
                    if (!provider) {
                        throw new Error('Provider not found');
                    }

                    const response = await fetch(provider.webhook_url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            [provider.signature_header]: 'test-signature'
                        },
                        body: this.testData
                    });

                    this.lastTest = new Date().toLocaleString();
                    this.testStatus = response.ok ? 'Success' : 'Failed';
                    
                    PaymentSystem.Utils.showNotification(
                        `Test webhook ${response.ok ? 'sent successfully' : 'failed'}`,
                        response.ok ? 'success' : 'error',
                        response.ok ? 'check_circle' : 'error'
                    );
                    
                    this.showTestModal = false;
                } catch (error) {
                    console.error('Test webhook failed:', error);
                    this.testStatus = 'Error';
                    PaymentSystem.Utils.showNotification('Failed to send test webhook', 'error', 'error');
                } finally {
                    this.testLoading = false;
                }
            },

            copyToClipboard(text) {
                PaymentSystem.Utils.copyToClipboard(text);
            }
        }
    },

    /**
     * Payment Form Component
     */
    paymentForm: function() {
        return {
            formData: {
                amount: '',
                currency: 'USD',
                provider: '',
                callback_url: ''
            },
            loading: false,
            errors: {},
            currencies: [],
            providers: [],

            async init() {
                await this.loadFormData();
            },

            async loadFormData() {
                try {
                    const [currenciesResponse, providersResponse] = await Promise.all([
                        fetch('/payments/api/currencies/supported/'),
                        fetch('/api/payments/webhooks/providers/')
                    ]);

                    const currenciesData = await currenciesResponse.json();
                    const providersData = await providersResponse.json();

                    this.currencies = currenciesData.currencies || [];
                    this.providers = providersData.providers || [];
                } catch (error) {
                    console.error('Failed to load form data:', error);
                    PaymentSystem.Utils.showNotification('Failed to load form data', 'error');
                }
            },

            validateForm() {
                this.errors = {};

                if (!this.formData.amount || parseFloat(this.formData.amount) <= 0) {
                    this.errors.amount = 'Amount must be greater than 0';
                }

                if (!this.formData.currency) {
                    this.errors.currency = 'Currency is required';
                }

                if (!this.formData.provider) {
                    this.errors.provider = 'Provider is required';
                }

                if (this.formData.callback_url && !PaymentSystem.Utils.isValidUrl(this.formData.callback_url)) {
                    this.errors.callback_url = 'Invalid URL format';
                }

                return Object.keys(this.errors).length === 0;
            },

            async submitForm() {
                if (!this.validateForm()) {
                    PaymentSystem.Utils.showNotification('Please fix form errors', 'warning', 'warning');
                    return;
                }

                this.loading = true;
                try {
                    const response = await fetch('/payments/api/payments/create/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        },
                        body: JSON.stringify(this.formData)
                    });

                    const data = await response.json();

                    if (response.ok && data.success) {
                        PaymentSystem.Utils.showNotification('Payment created successfully', 'success', 'check_circle');
                        // Redirect to payment status page
                        window.location.href = `/payments/status/${data.payment.id}/`;
                    } else {
                        throw new Error(data.error || 'Failed to create payment');
                    }
                } catch (error) {
                    console.error('Payment creation failed:', error);
                    PaymentSystem.Utils.showNotification(error.message, 'error', 'error');
                } finally {
                    this.loading = false;
                }
            }
        }
    },

    /**
     * Data Table Component
     */
    dataTable: function(config = {}) {
        return {
            data: [],
            loading: true,
            currentPage: 1,
            perPage: config.perPage || 10,
            totalPages: 1,
            totalItems: 0,
            sortField: config.defaultSort || 'created_at',
            sortDirection: 'desc',
            searchQuery: '',
            filters: {},
            selectedItems: [],

            async init() {
                await this.loadData();
            },

            async loadData() {
                this.loading = true;
                try {
                    const params = new URLSearchParams({
                        page: this.currentPage,
                        per_page: this.perPage,
                        sort: this.sortField,
                        direction: this.sortDirection,
                        search: this.searchQuery,
                        ...this.filters
                    });

                    const response = await fetch(`${config.apiUrl}?${params}`);
                    const data = await response.json();

                    if (response.ok) {
                        this.data = data.results || data.data || [];
                        this.totalPages = Math.ceil((data.count || data.total || 0) / this.perPage);
                        this.totalItems = data.count || data.total || 0;
                    } else {
                        throw new Error(data.error || 'Failed to load data');
                    }
                } catch (error) {
                    console.error('Failed to load table data:', error);
                    PaymentSystem.Utils.showNotification('Failed to load data', 'error');
                } finally {
                    this.loading = false;
                }
            },

            async sort(field) {
                if (this.sortField === field) {
                    this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    this.sortField = field;
                    this.sortDirection = 'asc';
                }
                this.currentPage = 1;
                await this.loadData();
            },

            async search() {
                this.currentPage = 1;
                await this.loadData();
            },

            async goToPage(page) {
                if (page >= 1 && page <= this.totalPages) {
                    this.currentPage = page;
                    await this.loadData();
                }
            },

            async applyFilters(newFilters) {
                this.filters = { ...this.filters, ...newFilters };
                this.currentPage = 1;
                await this.loadData();
            },

            toggleSelection(item) {
                const index = this.selectedItems.findIndex(selected => selected.id === item.id);
                if (index > -1) {
                    this.selectedItems.splice(index, 1);
                } else {
                    this.selectedItems.push(item);
                }
            },

            selectAll() {
                if (this.selectedItems.length === this.data.length) {
                    this.selectedItems = [];
                } else {
                    this.selectedItems = [...this.data];
                }
            },

            isSelected(item) {
                return this.selectedItems.some(selected => selected.id === item.id);
            }
        }
    },

    /**
     * Modal Component
     */
    modal: function(config = {}) {
        return {
            show: false,
            title: config.title || 'Modal',
            size: config.size || 'md',
            closable: config.closable !== false,

            open() {
                this.show = true;
                document.body.style.overflow = 'hidden';
            },

            close() {
                if (this.closable) {
                    this.show = false;
                    document.body.style.overflow = '';
                }
            },

            onEscape(event) {
                if (event.key === 'Escape' && this.closable) {
                    this.close();
                }
            }
        }
    },

    /**
     * Status Monitor Component
     */
    statusMonitor: function(config = {}) {
        return {
            status: 'checking',
            lastCheck: null,
            interval: null,
            checkUrl: config.checkUrl,
            intervalMs: config.intervalMs || 30000,

            async init() {
                await this.checkStatus();
                this.startMonitoring();
            },

            async checkStatus() {
                try {
                    const response = await fetch(this.checkUrl);
                    const data = await response.json();
                    
                    this.status = data.status || 'unknown';
                    this.lastCheck = new Date().toLocaleString();
                } catch (error) {
                    console.error('Status check failed:', error);
                    this.status = 'error';
                    this.lastCheck = new Date().toLocaleString();
                }
            },

            startMonitoring() {
                if (this.interval) {
                    clearInterval(this.interval);
                }
                
                this.interval = setInterval(() => {
                    this.checkStatus();
                }, this.intervalMs);
            },

            stopMonitoring() {
                if (this.interval) {
                    clearInterval(this.interval);
                    this.interval = null;
                }
            },

            getStatusIcon() {
                return PaymentSystem.Utils.getStatusIcon(this.status);
            },

            getStatusClass() {
                return PaymentSystem.Utils.getStatusBadgeClass(this.status);
            }
        }
    }
};

/**
 * Global Alpine.js data functions
 */
window.webhookDashboard = PaymentSystem.Components.webhookDashboard;
window.paymentForm = PaymentSystem.Components.paymentForm;
window.dataTable = PaymentSystem.Components.dataTable;
window.modal = PaymentSystem.Components.modal;
window.statusMonitor = PaymentSystem.Components.statusMonitor;

/**
 * Initialize components on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add global click handlers for common actions
    document.addEventListener('click', function(e) {
        // Handle refresh buttons
        if (e.target.matches('[data-refresh]')) {
            const target = e.target.getAttribute('data-refresh');
            if (target === 'page') {
                location.reload();
            } else {
                // Trigger Alpine.js refresh method if available
                const component = e.target.closest('[x-data]');
                if (component && component._x_dataStack && component._x_dataStack[0].refreshData) {
                    component._x_dataStack[0].refreshData();
                }
            }
        }

        // Handle modal triggers
        if (e.target.matches('[data-modal]')) {
            const modalId = e.target.getAttribute('data-modal');
            const modal = document.querySelector(`[data-modal-id="${modalId}"]`);
            if (modal && modal._x_dataStack && modal._x_dataStack[0].open) {
                modal._x_dataStack[0].open();
            }
        }
    });

    // Add global form validation
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.hasAttribute('data-validate')) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('border-red-500');
                    isValid = false;
                } else {
                    field.classList.remove('border-red-500');
                }
            });

            if (!isValid) {
                e.preventDefault();
                PaymentSystem.Utils.showNotification('Please fill in all required fields', 'warning', 'warning');
            }
        }
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PaymentSystem.Components;
}
