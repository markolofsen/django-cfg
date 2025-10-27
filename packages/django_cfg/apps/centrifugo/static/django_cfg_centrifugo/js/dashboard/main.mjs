/**
 * Main Centrifugo Dashboard Controller
 * Orchestrates all dashboard modules and handles tab navigation
 */
import { OverviewModule } from './overview.mjs';
import { UsageGuideModule } from './testing.mjs';
import { LiveChannelsModule } from './live_channels.mjs';
import { LiveTestingModule } from './live_testing.mjs';
import { WebSocketModule } from './websocket.mjs';

class CentrifugoDashboard {
    constructor() {
        this.api = window.centrifugoAPI;
        this.currentTab = 'overview';
        this.autoRefresh = true;
        this.refreshInterval = null;
        this.refreshRate = 5000; // 5 seconds

        // Initialize modules
        this.overviewModule = new OverviewModule(this.api, this);
        this.usageGuideModule = new UsageGuideModule(this.api, this);
        this.liveChannelsModule = new LiveChannelsModule(this.api, this);
        this.liveTestingModule = new LiveTestingModule(this.api, this);
        this.websocketModule = new WebSocketModule(this);
    }

    init() {
        console.log('=� Centrifugo Dashboard initializing...');
        this.setupEventListeners();
        this.usageGuideModule.init();
        this.loadInitialData();
        this.startAutoRefresh();

        // Initialize WebSocket for real-time updates
        this.websocketModule.init();
        console.log(' Centrifugo Dashboard initialized');
    }

    isValidTab(tabName) {
        const validTabs = ['overview', 'usage-guide', 'live-channels'];
        return validTabs.includes(tabName);
    }

    setupEventListeners() {
        // Check URL hash on page load
        const hash = window.location.hash.slice(1); // Remove #
        if (hash && this.isValidTab(hash)) {
            this.currentTab = hash;
        }

        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.currentTarget.dataset.tab;
                this.switchTab(tabName);
            });
        });

        // Handle browser back/forward buttons
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.slice(1);
            if (hash && this.isValidTab(hash)) {
                this.switchTab(hash, false); // Don't update hash again
            }
        });

        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.checked = this.autoRefresh;
            autoRefreshToggle.addEventListener('change', (e) => {
                this.autoRefresh = e.target.checked;
                if (this.autoRefresh) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }
    }

    switchTab(tabName, updateHash = true) {
        console.log('Switching to tab:', tabName);

        // Update URL hash
        if (updateHash) {
            window.history.pushState(null, '', `#${tabName}`);
        }

        document.querySelectorAll('.tab-button').forEach(btn => {
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active', 'text-purple-600', 'dark:text-purple-400', 'border-purple-600', 'dark:border-purple-400');
                btn.classList.remove('text-gray-600', 'dark:text-gray-400', 'border-transparent');
            } else {
                btn.classList.remove('active', 'text-purple-600', 'dark:text-purple-400', 'border-purple-600', 'dark:border-purple-400');
                btn.classList.add('text-gray-600', 'dark:text-gray-400', 'border-transparent');
            }
        });

        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.add('hidden');
        });

        const activePanel = document.getElementById(tabName + '-tab');
        if (activePanel) {
            activePanel.classList.remove('hidden');
        }

        this.currentTab = tabName;

        // Update connection status when switching to usage-guide tab
        if (tabName === 'usage-guide' && this.liveTestingModule) {
            this.liveTestingModule.updateConnectionStatus(
                this.liveTestingModule.centrifuge !== null
            );
        }

        this.loadTabData(tabName);
    }

    async loadInitialData() {
        console.log('Loading initial data...');

        // If tab was set from hash, switch to it
        if (this.currentTab !== 'overview') {
            this.switchTab(this.currentTab, false);
        }

        await this.loadHealthStatus();
        await this.loadTabData(this.currentTab);
    }

    async loadTabData(tabName) {
        console.log('Loading data for tab:', tabName);

        try {
            // Always update overview stats (for stat cards at top)
            await this.overviewModule.loadOverviewStats();

            if (tabName === 'usage-guide') {
                // Usage guide tab doesn't need data loading (static content)
                return;
            } else if (tabName === 'live-channels') {
                // Load live channels from Centrifugo server
                await this.liveChannelsModule.loadLiveChannels();
            } else {
                await this.overviewModule.loadData(tabName);
            }

            this.updateLastUpdate();
        } catch (error) {
            console.error('Error loading tab data:', error);
        }
    }

    async loadHealthStatus() {
        try {
            const health = await this.api.centrifugoAdminApiMonitorHealthRetrieve();

            if (health) {
                const indicator = document.getElementById('health-indicator');
                if (indicator) {
                    // Health status is based on whether wrapper_url is configured
                    const isHealthy = health.status === 'healthy' && health.wrapper_url;
                    const statusColor = isHealthy ? 'bg-green-500' : 'bg-red-500';
                    const statusText = isHealthy ? 'Configured' : 'Not Configured';
                    const html = '<span class="pulse-dot w-2 h-2 ' + statusColor + ' rounded-full"></span>' +
                                 '<span class="text-xs font-medium text-gray-600 dark:text-gray-400">' + statusText + '</span>';
                    indicator.innerHTML = html;
                }

                this.updateSystemStatus(health);
            }

            // Also load live server info
            await this.loadServerInfo();
        } catch (error) {
            console.error('Error loading health status:', error);
        }
    }

    async loadServerInfo() {
        try {
            console.log('Loading Centrifugo server info...');

            // Call Server API to get live stats
            const response = await this.api.centrifugoAdminApiServerInfoCreate();

            if (response && response.result && response.result.nodes && response.result.nodes.length > 0) {
                const node = response.result.nodes[0]; // First node

                // Update server version and uptime
                this.updateElement('server-version-text', `${node.name} v${node.version}`);
                this.updateElement('server-uptime-text', `Uptime: ${this.formatUptime(node.uptime)}`);

                // Update live connection stats
                this.updateElement('live-clients-count', node.num_clients.toLocaleString());
                this.updateElement('live-users-count', node.num_users.toLocaleString());
                this.updateElement('live-channels-count', node.num_channels.toLocaleString());
                this.updateElement('live-subs-count', node.num_subs.toLocaleString());

                // Update server status icon
                const serverIcon = document.getElementById('server-status-icon');
                if (serverIcon) {
                    serverIcon.className = 'material-icons flex-shrink-0 text-2xl text-green-500';
                    serverIcon.textContent = 'check_circle';
                }

                console.log('Server info loaded:', node);
            } else if (response && response.error) {
                console.error('Server API error:', response.error);
                this.showServerError(response.error.message);
            }
        } catch (error) {
            console.error('Failed to load server info:', error);
            this.showServerError('Failed to connect to Centrifugo server');
        }
    }

    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);

        if (days > 0) {
            return `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else {
            return `${minutes}m`;
        }
    }

    showServerError(message) {
        this.updateElement('server-version-text', 'Offline');
        this.updateElement('server-uptime-text', message);
        this.updateElement('live-clients-count', '?');
        this.updateElement('live-users-count', '?');
        this.updateElement('live-channels-count', '?');
        this.updateElement('live-subs-count', '?');

        const serverIcon = document.getElementById('server-status-icon');
        if (serverIcon) {
            serverIcon.className = 'material-icons flex-shrink-0 text-2xl text-red-500';
            serverIcon.textContent = 'error';
        }
    }

    updateSystemStatus(health) {
        const statusContainer = document.getElementById('system-status');
        if (!statusContainer) return;

        // Wrapper status
        const wrapperColor = health.wrapper_url ? 'text-green-500' : 'text-gray-500';
        const wrapperIcon = health.wrapper_url ? 'link' : 'link_off';

        // Configuration status (API key)
        const configColor = health.has_api_key ? 'text-green-500' : 'text-yellow-500';
        const configIcon = health.has_api_key ? 'vpn_key' : 'warning';
        const configStatus = health.has_api_key ? 'API Key Configured' : 'No API Key';

        let html = '<div class="flex items-start gap-3">';
        html += '<span class="material-icons flex-shrink-0 text-2xl ' + wrapperColor + '">' + wrapperIcon + '</span>';
        html += '<div class="min-w-0">';
        html += '<p class="text-sm font-medium text-gray-900 dark:text-white">Centrifugo Wrapper</p>';
        html += '<p class="text-xs text-gray-600 dark:text-gray-400 break-all">' + (health.wrapper_url || 'Not configured') + '</p>';
        html += '</div></div>';

        html += '<div class="flex items-start gap-3">';
        html += '<span class="material-icons flex-shrink-0 text-2xl ' + configColor + '">' + configIcon + '</span>';
        html += '<div class="min-w-0">';
        html += '<p class="text-sm font-medium text-gray-900 dark:text-white">Configuration</p>';
        html += '<p class="text-xs text-gray-600 dark:text-gray-400">' + configStatus + '</p>';
        html += '</div></div>';

        statusContainer.innerHTML = html;
    }

    updateLastUpdate() {
        const element = document.getElementById('last-update');
        if (element) {
            const now = new Date();
            element.textContent = 'Last updated: ' + now.toLocaleTimeString();
        }
    }

    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.refreshInterval = setInterval(() => {
            if (this.autoRefresh) {
                this.loadHealthStatus();

                // Don't refresh static tabs (usage-guide)
                if (this.currentTab !== 'usage-guide') {
                    this.loadTabData(this.currentTab);
                }
            }
        }, this.refreshRate);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
}

async function initializeDashboard() {
    console.log('DOM loaded, waiting for CentrifugoAPI...');

    let attempts = 0;
    const maxAttempts = 100;

    while (!window.centrifugoAPI && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 50));
        attempts++;
    }

    if (!window.centrifugoAPI) {
        console.error('L CentrifugoAPI failed to load after 5 seconds');
        return;
    }

    console.log(' CentrifugoAPI ready, initializing dashboard...');
    window.centrifugoDashboard = new CentrifugoDashboard();
    window.centrifugoDashboard.init();
}

document.addEventListener('DOMContentLoaded', initializeDashboard);

export default CentrifugoDashboard;
