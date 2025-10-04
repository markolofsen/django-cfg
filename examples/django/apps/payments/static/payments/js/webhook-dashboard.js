/**
 * Webhook Dashboard Component
 * Handles webhook events monitoring and testing
 */
function webhookDashboard() {
    return {
        loading: false,
        testLoading: false,
        events: [],
        filters: {
            event_type: '',
            status: ''
        },
        stats: {
            total: 0,
            successful: 0,
            failed: 0,
            successRate: 0
        },
        testForm: {
            url: '',
            event_type: ''
        },
        showEventModal: false,
        selectedEvent: null,

        get filteredEvents() {
            let filtered = this.events;
            
            if (this.filters.event_type) {
                filtered = filtered.filter(event => event.event_type === this.filters.event_type);
            }
            
            if (this.filters.status) {
                filtered = filtered.filter(event => event.status === this.filters.status);
            }
            
            return filtered;
        },

        async init() {
            await this.loadEvents();
            await this.loadStats();
            // Auto-refresh every 30 seconds
            setInterval(() => this.refreshEvents(), 30000);
        },

        async loadEvents() {
            this.loading = true;
            try {
                const response = await PaymentAPI.admin.webhooks.events.list();
                this.events = response.events || [];
                this.pagination = {
                    total: response.total || 0,
                    page: response.page || 1,
                    per_page: response.per_page || 50,
                    has_next: response.has_next || false,
                    has_previous: response.has_previous || false
                };
            } catch (error) {
                console.error('Failed to load events:', error);
                this.events = [];
                PaymentAPI.utils.showNotification('Failed to load webhook events', 'error');
            } finally {
                this.loading = false;
            }
        },

        async loadStats() {
            try {
                this.stats = await PaymentAPI.admin.webhooks.stats();
            } catch (error) {
                console.error('Failed to load stats:', error);
                // Set default stats on error
                this.stats = {
                    total: 0,
                    successful: 0,
                    failed: 0,
                    successRate: 0
                };
                PaymentAPI.utils.showNotification('Failed to load webhook stats', 'error');
            }
        },

        async refreshEvents() {
            await this.loadEvents();
            await this.loadStats();
        },

        async clearEvents() {
            if (confirm('Are you sure you want to clear all events?')) {
                try {
                    await PaymentAPI.admin.webhooks.events.clearAll(1);
                    this.events = [];
                    await this.loadStats();
                    PaymentAPI.utils.showNotification('All events cleared', 'success');
                } catch (error) {
                    console.error('Failed to clear events:', error);
                    PaymentAPI.utils.showNotification('Failed to clear events', 'error');
                }
            }
        },

        async testWebhook() {
            this.testLoading = true;
            try {
                await PaymentAPI.admin.webhookTest.send(this.testForm.url, this.testForm.event_type);
                PaymentAPI.utils.showNotification('Test webhook sent successfully!', 'success');
                this.testForm = { url: '', event_type: '' };
                await this.refreshEvents();
            } catch (error) {
                console.error('Failed to test webhook:', error);
                PaymentAPI.utils.showNotification('Failed to send test webhook', 'error');
            } finally {
                this.testLoading = false;
            }
        },

        async retryEvent(eventId) {
            try {
                await PaymentAPI.admin.webhooks.events.retry(1, eventId);
                await this.refreshEvents();
                PaymentAPI.utils.showNotification('Event retried', 'success');
            } catch (error) {
                console.error('Failed to retry event:', error);
                PaymentAPI.utils.showNotification('Failed to retry event', 'error');
            }
        },

        async retryFailedEvents() {
            try {
                await PaymentAPI.admin.webhooks.events.retryFailed(1);
                await this.refreshEvents();
                PaymentAPI.utils.showNotification('Failed events retried', 'success');
            } catch (error) {
                console.error('Failed to retry failed events:', error);
                PaymentAPI.utils.showNotification('Failed to retry events', 'error');
            }
        },

        viewEvent(event) {
            this.selectedEvent = event;
            this.showEventModal = true;
        },

        applyFilters() {
            // Filters are applied automatically via computed property
        },

        formatDate(dateString) {
            return PaymentAPI.utils.formatDate(dateString);
        }
    };
}
