/**
 * Payment List Component
 * Handles payment listing, filtering, and pagination
 */
function paymentList() {
    return {
        loading: false,
        payments: [],
        filters: {
            search: '',
            status: ''
        },
        currentPage: 1,
        pageSize: 10,

        get filteredPayments() {
            let filtered = this.payments;
            
            if (this.filters.search) {
                const search = this.filters.search.toLowerCase();
                filtered = filtered.filter(payment => 
                    payment.id.toLowerCase().includes(search) ||
                    payment.external_id?.toLowerCase().includes(search) ||
                    payment.provider.toLowerCase().includes(search)
                );
            }
            
            if (this.filters.status) {
                filtered = filtered.filter(payment => payment.status === this.filters.status);
            }
            
            return filtered;
        },

        get paginatedPayments() {
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return this.filteredPayments.slice(start, end);
        },

        async init() {
            await this.loadPayments();
            // Auto-refresh every 30 seconds
            setInterval(() => this.loadPayments(), 30000);
        },

        async loadPayments() {
            this.loading = true;
            try {
                const response = await PaymentAPI.admin.payments.list(this.filters);
                this.payments = response.payments || response.results || [];
                this.pagination = {
                    total: response.total || response.count || 0,
                    page: response.page || 1,
                    per_page: response.per_page || 50,
                    has_next: response.has_next || false,
                    has_previous: response.has_previous || false
                };
            } catch (error) {
                console.error('Failed to load payments:', error);
                this.payments = [];
                PaymentAPI.utils.showNotification('Failed to load payments', 'error');
            } finally {
                this.loading = false;
            }
        },

        async refreshPayments() {
            await this.loadPayments();
            PaymentAPI.utils.showNotification('Payments refreshed', 'success');
        },

        async refreshPayment(paymentId) {
            try {
                const updatedPayment = await PaymentAPI.payments.get(paymentId);
                const index = this.payments.findIndex(p => p.id === paymentId);
                if (index !== -1) {
                    this.payments[index] = updatedPayment;
                }
                PaymentAPI.utils.showNotification('Payment updated', 'success');
            } catch (error) {
                console.error('Failed to refresh payment:', error);
                PaymentAPI.utils.showNotification('Failed to refresh payment', 'error');
            }
        },

        applyFilters() {
            this.currentPage = 1;
        },

        formatDate(dateString) {
            return PaymentAPI.utils.formatDate(dateString);
        }
    };
}
