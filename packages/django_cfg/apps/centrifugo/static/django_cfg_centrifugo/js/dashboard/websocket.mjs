/**
 * WebSocket Real-time Updates Module
 * Subscribes to Centrifugo channels for live dashboard updates
 */

export class WebSocketModule {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.centrifuge = null;
        this.subscription = null;
        this.dashboardChannel = 'centrifugo#dashboard';
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    async init() {
        console.log('🔌 Initializing WebSocket connection...');

        try {
            // Get Centrifugo connection token
            const tokenResponse = await this.dashboard.api.centrifugoAdminApiServerAuthTokenCreate();

            if (!tokenResponse || !tokenResponse.token) {
                console.error('❌ Failed to get connection token');
                return;
            }

            const config = tokenResponse.config || {};
            const wsUrl = config.centrifugo_url || 'ws://localhost:8002/connection/websocket';

            console.log('🔌 Connecting to:', wsUrl);

            // Initialize Centrifuge client
            this.centrifuge = new Centrifuge(wsUrl, {
                token: tokenResponse.token,
                debug: true,
            });

            // Setup event handlers
            this.setupEventHandlers();

            // Connect
            this.centrifuge.connect();

        } catch (error) {
            console.error('❌ WebSocket initialization error:', error);
        }
    }

    setupEventHandlers() {
        // Connection events
        this.centrifuge.on('connected', (ctx) => {
            console.log('✅ WebSocket connected:', ctx);
            this.reconnectAttempts = 0;
            this.subscribeToDashboard();
            this.updateConnectionStatus(true);
        });

        this.centrifuge.on('disconnected', (ctx) => {
            console.log('⚠️ WebSocket disconnected:', ctx);
            this.updateConnectionStatus(false);

            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                console.log(`🔄 Reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            }
        });

        this.centrifuge.on('error', (ctx) => {
            console.error('❌ WebSocket error:', ctx);
        });
    }

    subscribeToDashboard() {
        console.log('📡 Subscribing to dashboard channel:', this.dashboardChannel);

        this.subscription = this.centrifuge.newSubscription(this.dashboardChannel);

        this.subscription.on('publication', (ctx) => {
            console.log('📨 Dashboard update received:', ctx.data);
            this.handleDashboardUpdate(ctx.data);
        });

        this.subscription.on('subscribed', (ctx) => {
            console.log('✅ Subscribed to dashboard channel');
        });

        this.subscription.on('error', (ctx) => {
            console.error('❌ Subscription error:', ctx);
        });

        this.subscription.subscribe();
    }

    handleDashboardUpdate(data) {
        const { type } = data;

        switch (type) {
            case 'new_publish':
                this.handleNewPublish(data.publish);
                break;

            case 'status_change':
                this.handleStatusChange(data.publish);
                break;

            case 'stats_update':
                this.handleStatsUpdate();
                break;

            default:
                console.log('⚠️ Unknown message type:', type);
        }
    }

    handleNewPublish(publish) {
        console.log('🆕 New publish:', publish);

        // Show notification
        this.showNotification('New Publish', `Channel: ${publish.channel}`);

        // Refresh overview stats
        if (this.dashboard.overviewModule) {
            this.dashboard.overviewModule.loadOverviewStats();
        }

        // If on overview tab, refresh data
        if (this.dashboard.currentTab === 'overview') {
            this.dashboard.overviewModule.loadData('overview');
        }
    }

    handleStatusChange(publish) {
        console.log('🔄 Status change:', publish);

        // Refresh overview stats and charts
        if (this.dashboard.overviewModule) {
            this.dashboard.overviewModule.loadOverviewStats();

            if (this.dashboard.currentTab === 'overview') {
                this.dashboard.overviewModule.loadData('overview');
            }
        }
    }

    handleStatsUpdate() {
        console.log('📊 Stats update requested');

        // Full refresh
        this.dashboard.loadTabData(this.dashboard.currentTab);
    }

    showNotification(title, message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-purple-600 text-white px-4 py-3 rounded-lg shadow-lg z-50 animate-slide-up';
        toast.innerHTML = `
            <div class="flex items-center gap-2">
                <span class="material-icons text-sm">notifications</span>
                <div>
                    <p class="font-semibold text-sm">${title}</p>
                    <p class="text-xs opacity-90">${message}</p>
                </div>
            </div>
        `;

        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('header-ws-status');
        if (!indicator) return;

        // Keep container classes, only update inner content
        const baseClasses = 'flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700';

        if (connected) {
            indicator.className = baseClasses;
            indicator.innerHTML = `
                <span class="pulse-dot w-2 h-2 bg-green-500 rounded-full"></span>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Live Updates</span>
            `;
        } else {
            indicator.className = baseClasses;
            indicator.innerHTML = `
                <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Reconnecting...</span>
            `;
        }
    }

    disconnect() {
        if (this.subscription) {
            this.subscription.unsubscribe();
        }

        if (this.centrifuge) {
            this.centrifuge.disconnect();
        }

        console.log('🔌 WebSocket disconnected');
    }
}
