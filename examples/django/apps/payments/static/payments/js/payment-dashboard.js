/**
 * Payment Dashboard Component
 * Handles dashboard data loading and display
 */
function paymentDashboard() {
    return {
        loading: false,
        stats: {
            total: 0,
            successful: 0,
            pending: 0,
            failed: 0
        },
        recentPayments: [],
        recentActivity: [
            { id: 1, message: 'Payment created', time: '2 minutes ago' },
            { id: 2, message: 'Webhook received', time: '5 minutes ago' },
            { id: 3, message: 'Payment completed', time: '10 minutes ago' }
        ],

        async init() {
            await this.loadDashboardData();
            // Auto-refresh every 60 seconds
            setInterval(() => this.loadDashboardData(), 60000);
        },

        async loadDashboardData() {
            this.loading = true;
            try {
                // Load dashboard data using API client
                const [overview, recentPayments] = await Promise.all([
                    PaymentAPI.dashboard.overview(),
                    PaymentAPI.dashboard.recentPayments(5)
                ]);

                this.stats = overview.stats || this.stats;
                this.recentPayments = recentPayments || [];
            } catch (error) {
                console.error('Failed to load dashboard data:', error);
                PaymentAPI.utils.showNotification('Failed to load dashboard data', 'error');
            } finally {
                this.loading = false;
            }
        },

        async refreshDashboard() {
            await this.loadDashboardData();
        }
    };
}
