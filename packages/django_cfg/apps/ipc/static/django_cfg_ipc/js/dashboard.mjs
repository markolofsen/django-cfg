/**
 * RPC Dashboard JavaScript Module
 *
 * Uses generated MJS API client for all API calls
 *
 * Handles:
 * - Tab switching
 * - Auto-refresh
 * - Live data updates
 * - API communication via generated client
 */

import { ipcAPI } from '/static/js/api/ipc/index.mjs';

class RPCDashboard {
    constructor() {
        this.autoRefresh = true;
        this.refreshInterval = 5000; // 5 seconds
        this.intervalId = null;
        this.currentTab = 'overview';

        // Use the pre-instantiated API client
        this.api = ipcAPI;

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
                btn.classList.add('active', 'text-blue-600', 'dark:text-blue-400', 'border-blue-600', 'dark:border-blue-400');
                btn.classList.remove('text-gray-600', 'dark:text-gray-400', 'border-transparent');
            } else {
                btn.classList.remove('active', 'text-blue-600', 'dark:text-blue-400', 'border-blue-600', 'dark:border-blue-400');
                btn.classList.add('text-gray-600', 'dark:text-gray-400', 'border-transparent');
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
            await Promise.all([
                this.loadOverviewStats(),
                this.loadHealthStatus()
            ]);
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
            const stats = await this.api.ipcAdminApiMonitorOverviewRetrieve();

            if (stats) {
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
                        code.className = 'bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-blue-600 dark:text-blue-300';
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
            const health = await this.api.ipcAdminApiMonitorHealthRetrieve();

            if (health) {
                // Update health indicator
                const indicator = document.getElementById('health-indicator');
                if (indicator) {
                    const isHealthy = health.redis_connected && health.stream_exists;
                    indicator.innerHTML = `
                        <span class="pulse-dot w-2 h-2 ${isHealthy ? 'bg-green-500' : 'bg-red-500'} rounded-full"></span>
                        <span class="text-sm text-gray-700 dark:text-gray-300">${isHealthy ? 'Connected' : 'Disconnected'}</span>
                    `;
                }

                // Update system status section
                this.updateSystemStatus(health);
            }
        } catch (error) {
            console.error('Error loading health status:', error);
        }
    }

    updateSystemStatus(health) {
        const statusContainer = document.getElementById('system-status');
        if (!statusContainer) return;

        statusContainer.innerHTML = `
            <!-- Redis Status -->
            <div class="flex items-start gap-3">
                <span class="material-icons flex-shrink-0 text-2xl ${health.redis_connected ? 'text-green-500' : 'text-red-500'}">
                    ${health.redis_connected ? 'check_circle' : 'cancel'}
                </span>
                <div class="min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white">Redis</p>
                    <p class="text-xs text-gray-600 dark:text-gray-400">
                        ${health.redis_connected ? 'Connected (DB 2)' : 'Disconnected'}
                    </p>
                </div>
            </div>

            <!-- Stream Status -->
            <div class="flex items-start gap-3">
                <span class="material-icons flex-shrink-0 text-2xl ${health.stream_exists ? 'text-green-500' : 'text-gray-500'}">
                    ${health.stream_exists ? 'stream' : 'stream_off'}
                </span>
                <div class="min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white">Request Stream</p>
                    <p class="text-xs text-gray-600 dark:text-gray-400">
                        ${health.stream_exists ? `${health.stream_length} entries` : 'Not initialized'}
                    </p>
                </div>
            </div>

            <!-- Activity Status -->
            <div class="flex items-start gap-3">
                <span class="material-icons flex-shrink-0 text-2xl ${health.recent_activity ? 'text-green-500' : 'text-yellow-500'}">
                    ${health.recent_activity ? 'notifications_active' : 'notifications_paused'}
                </span>
                <div class="min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white">Recent Activity</p>
                    <p class="text-xs text-gray-600 dark:text-gray-400">
                        ${health.recent_activity ? 'Active (last 5 min)' : 'No recent activity'}
                    </p>
                </div>
            </div>
        `;
    }

    async loadRecentRequests() {
        try {
            const data = await this.api.ipcAdminApiMonitorRequestsRetrieve({ count: 50 });

            if (data) {
                const requests = data.requests || [];
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
                    <td colspan="4" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                        No recent requests found
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = requests.map(req => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-4 py-3 text-sm">
                    ${this.formatTimestamp(req.timestamp)}
                </td>
                <td class="px-4 py-3">
                    <code class="text-sm bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">${this.escapeHtml(req.method || 'unknown')}</code>
                </td>
                <td class="px-4 py-3 text-sm font-mono">
                    ${this.escapeHtml((req.correlation_id || '').substring(0, 8))}...
                </td>
                <td class="px-4 py-3 text-sm">
                    <details class="cursor-pointer">
                        <summary class="text-blue-600 dark:text-blue-400 hover:underline">View</summary>
                        <pre class="mt-2 text-xs bg-gray-100 dark:bg-gray-900 p-2 rounded overflow-auto max-h-40">${this.escapeHtml(JSON.stringify(req.params || {}, null, 2))}</pre>
                    </details>
                </td>
            </tr>
        `).join('');
    }

    async loadNotificationStats() {
        try {
            const stats = await this.api.ipcAdminApiMonitorNotificationsRetrieve();

            if (stats) {
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
                <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded">
                    <span>Total Sent</span>
                    <span class="text-2xl font-bold">${total}</span>
                </div>
                <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded">
                    <span>Delivery Rate</span>
                    <span class="text-2xl font-bold text-green-600 dark:text-green-400">${stats.delivery_rate || 0}%</span>
                </div>
                <div>
                    <h4 class="text-md font-semibold mb-3">By Type</h4>
                    <div class="space-y-2">
                        ${Object.entries(byType).map(([type, count]) => `
                            <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
                                <span>${this.escapeHtml(type)}</span>
                                <span class="font-medium">${count}</span>
                            </div>
                        `).join('') || '<p class="text-gray-500 dark:text-gray-400">No data available</p>'}
                    </div>
                </div>
                ${stats.recent && stats.recent.length > 0 ? `
                    <div>
                        <h4 class="text-md font-semibold mb-3">Recent Notifications</h4>
                        <div class="space-y-2">
                            ${stats.recent.slice(0, 5).map(notif => `
                                <div class="p-3 bg-gray-50 dark:bg-gray-700 rounded">
                                    <div class="flex justify-between items-start">
                                        <span class="text-sm">${this.escapeHtml(notif.type || 'unknown')}</span>
                                        <span class="text-xs text-gray-500 dark:text-gray-400">${this.formatTimestamp(notif.timestamp)}</span>
                                    </div>
                                    ${notif.message ? `<p class="text-xs text-gray-600 dark:text-gray-400 mt-1">${this.escapeHtml(notif.message)}</p>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    async loadMethodStats() {
        try {
            const data = await this.api.ipcAdminApiMonitorMethodsRetrieve();

            if (data) {
                const methods = data.methods || [];
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
                    <td colspan="4" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                        No method data available
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = methods.map(method => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-4 py-3">
                    <code class="text-sm bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">${this.escapeHtml(method.method)}</code>
                </td>
                <td class="px-4 py-3 text-sm font-medium">${method.count}</td>
                <td class="px-4 py-3 text-sm">${method.percentage}%</td>
                <td class="px-4 py-3 text-sm">${method.avg_time_ms || method.avg_time || 0}ms</td>
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

    escapeHtml(unsafe) {
        const div = document.createElement('div');
        div.textContent = unsafe;
        return div.innerHTML;
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
        // Could show a toast notification here
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.rpcDashboard = new RPCDashboard();
});

// Export for debugging
export default RPCDashboard;
