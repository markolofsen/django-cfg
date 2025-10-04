/**
 * RPC Dashboard JavaScript
 *
 * Handles:
 * - Tab switching
 * - Auto-refresh
 * - Live data updates
 * - API communication
 */

class RPCDashboard {
    constructor() {
        this.autoRefresh = true;
        this.refreshInterval = 5000; // 5 seconds
        this.intervalId = null;
        this.currentTab = 'overview';

        // Get API base URL from data attribute (supports custom mounting)
        this.apiBase = document.body.dataset.apiBase || '/admin/rpc/api';
        // Clean up trailing slash if present
        this.apiBase = this.apiBase.replace(/\/$/, '');

        this.init();
    }

    init() {
        console.log('🚀 RPC Dashboard initializing...');

        // Setup tab switching
        this.setupTabs();

        // Setup auto-refresh toggle
        this.setupAutoRefresh();

        // Initial data load
        this.loadAllData();

        // Start auto-refresh
        this.startAutoRefresh();

        console.log('✅ RPC Dashboard initialized');
    }

    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');

        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active', 'text-blue-400', 'border-blue-400');
                btn.classList.remove('text-gray-400', 'border-transparent');
            } else {
                btn.classList.remove('active', 'text-blue-400', 'border-blue-400');
                btn.classList.add('text-gray-400', 'border-transparent');
            }
        });

        // Update panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.add('hidden');
        });

        const activePanel = document.getElementById(`${tabName}-tab`);
        if (activePanel) {
            activePanel.classList.remove('hidden');
        }

        this.currentTab = tabName;

        // Load tab-specific data
        this.loadTabData(tabName);
    }

    setupAutoRefresh() {
        const toggle = document.getElementById('auto-refresh-toggle');

        if (toggle) {
            toggle.checked = this.autoRefresh;

            toggle.addEventListener('change', (e) => {
                this.autoRefresh = e.target.checked;

                if (this.autoRefresh) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }
    }

    startAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }

        this.intervalId = setInterval(() => {
            if (this.autoRefresh) {
                this.loadAllData();
            }
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    async loadAllData() {
        try {
            await this.loadOverviewStats();
            await this.loadHealthStatus();
            await this.loadTabData(this.currentTab);
            this.updateLastUpdate();
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load data');
        }
    }

    async loadTabData(tabName) {
        switch (tabName) {
            case 'overview':
                // Already loaded in loadOverviewStats
                break;
            case 'requests':
                await this.loadRecentRequests();
                break;
            case 'notifications':
                await this.loadNotificationStats();
                break;
            case 'methods':
                await this.loadMethodStats();
                break;
        }
    }

    async loadOverviewStats() {
        try {
            const response = await fetch(`${this.apiBase}/overview/`);
            const data = await response.json();

            if (data.success) {
                const stats = data.data;

                // Update stats cards
                this.updateElement('total-requests', stats.total_requests_today || 0);
                this.updateElement('active-methods-count', stats.active_methods?.length || 0);
                this.updateElement('avg-response-time', (stats.avg_response_time_ms || 0).toFixed(0));
                this.updateElement('success-rate', (stats.success_rate || 0).toFixed(1));

                // Update top method (XSS-safe)
                if (stats.top_method) {
                    const topMethodElement = document.getElementById('top-method');
                    if (topMethodElement) {
                        const code = document.createElement('code');
                        code.className = 'bg-gray-700 px-2 py-1 rounded text-blue-300';
                        code.textContent = stats.top_method;  // Safe from XSS
                        topMethodElement.innerHTML = '';
                        topMethodElement.appendChild(code);
                    }
                }
            }
        } catch (error) {
            console.error('Error loading overview stats:', error);
        }
    }

    async loadHealthStatus() {
        try {
            const response = await fetch(`${this.apiBase}/health/`);
            const data = await response.json();

            if (data.success) {
                const health = data.data;

                // Update health indicator
                const indicator = document.getElementById('health-indicator');
                if (indicator) {
                    const isHealthy = health.redis_connected && health.stream_exists;
                    indicator.innerHTML = `
                        <span class="pulse-dot w-2 h-2 ${isHealthy ? 'bg-green-500' : 'bg-red-500'} rounded-full"></span>
                        <span class="text-sm text-gray-300">${isHealthy ? 'Connected' : 'Disconnected'}</span>
                    `;
                }
            }
        } catch (error) {
            console.error('Error loading health status:', error);
        }
    }

    async loadRecentRequests() {
        try {
            const response = await fetch(`${this.apiBase}/requests/?count=50`);
            const data = await response.json();

            if (data.success) {
                const requests = data.data.requests || [];
                this.renderRequestsTable(requests);
            }
        } catch (error) {
            console.error('Error loading recent requests:', error);
        }
    }

    renderRequestsTable(requests) {
        const tbody = document.getElementById('requests-table-body');
        if (!tbody) return;

        if (requests.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="px-4 py-8 text-center text-gray-400">
                        No recent requests found
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = requests.map(req => `
            <tr class="hover:bg-gray-700">
                <td class="px-4 py-3 text-sm text-gray-300">
                    ${this.formatTimestamp(req.timestamp)}
                </td>
                <td class="px-4 py-3">
                    <code class="text-sm bg-gray-700 px-2 py-1 rounded text-blue-300">${req.method || 'unknown'}</code>
                </td>
                <td class="px-4 py-3 text-sm text-gray-400 font-mono">
                    ${(req.correlation_id || '').substring(0, 8)}...
                </td>
                <td class="px-4 py-3 text-sm text-gray-400">
                    <details class="cursor-pointer">
                        <summary class="text-blue-400 hover:text-blue-300">View</summary>
                        <pre class="mt-2 text-xs bg-gray-900 p-2 rounded overflow-auto max-h-40">${JSON.stringify(req.params || {}, null, 2)}</pre>
                    </details>
                </td>
            </tr>
        `).join('');
    }

    async loadNotificationStats() {
        try {
            const response = await fetch(`${this.apiBase}/notifications/`);
            const data = await response.json();

            if (data.success) {
                const stats = data.data;
                this.renderNotificationStats(stats);
            }
        } catch (error) {
            console.error('Error loading notification stats:', error);
        }
    }

    renderNotificationStats(stats) {
        const container = document.getElementById('notification-stats-content');
        if (!container) return;

        const byType = stats.by_type || {};
        const total = stats.total_sent || 0;

        container.innerHTML = `
            <div class="space-y-4">
                <div class="flex items-center justify-between p-4 bg-gray-700 rounded">
                    <span class="text-gray-300">Total Sent</span>
                    <span class="text-2xl font-bold text-white">${total}</span>
                </div>
                <div class="flex items-center justify-between p-4 bg-gray-700 rounded">
                    <span class="text-gray-300">Delivery Rate</span>
                    <span class="text-2xl font-bold text-green-400">${stats.delivery_rate || 0}%</span>
                </div>
                <div>
                    <h4 class="text-md font-semibold text-white mb-3">By Type</h4>
                    <div class="space-y-2">
                        ${Object.entries(byType).map(([type, count]) => `
                            <div class="flex items-center justify-between p-3 bg-gray-700 rounded">
                                <span class="text-gray-300">${type}</span>
                                <span class="text-white font-medium">${count}</span>
                            </div>
                        `).join('') || '<p class="text-gray-400">No data available</p>'}
                    </div>
                </div>
            </div>
        `;
    }

    async loadMethodStats() {
        try {
            const response = await fetch(`${this.apiBase}/methods/`);
            const data = await response.json();

            if (data.success) {
                const methods = data.data.methods || [];
                this.renderMethodsTable(methods);
            }
        } catch (error) {
            console.error('Error loading method stats:', error);
        }
    }

    renderMethodsTable(methods) {
        const tbody = document.getElementById('methods-table-body');
        if (!tbody) return;

        if (methods.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="px-4 py-8 text-center text-gray-400">
                        No method data available
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = methods.map(method => `
            <tr class="hover:bg-gray-700">
                <td class="px-4 py-3">
                    <code class="text-sm bg-gray-700 px-2 py-1 rounded text-blue-300">${method.method}</code>
                </td>
                <td class="px-4 py-3 text-sm text-white font-medium">${method.count}</td>
                <td class="px-4 py-3 text-sm text-gray-300">${method.percentage}%</td>
                <td class="px-4 py-3 text-sm text-gray-300">${method.avg_time_ms}ms</td>
            </tr>
        `).join('');
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    formatTimestamp(isoString) {
        try {
            const date = new Date(isoString);
            return date.toLocaleTimeString();
        } catch {
            return 'N/A';
        }
    }

    updateLastUpdate() {
        const element = document.getElementById('last-update');
        if (element) {
            const now = new Date();
            element.textContent = `Last updated: ${now.toLocaleTimeString()}`;
        }
    }

    showError(message) {
        console.error('Dashboard error:', message);
        // TODO: Show error notification to user
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.rpcDashboard = new RPCDashboard();
});
