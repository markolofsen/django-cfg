/**
 * Main Tasks Dashboard Controller
 * Orchestrates all dashboard modules
 */
import { OverviewModule } from './overview.mjs';
import { QueuesModule } from './queues.mjs';
import { WorkersModule } from './workers.mjs';
import { TasksModule } from './tasks.mjs';

class TasksDashboard {
    constructor() {
        this.api = window.tasksAPI;
        this.currentTab = 'overview';
        this.refreshInterval = null;
        this.refreshRate = 30000; // 30 seconds
        
        // Initialize modules (pass reference to this dashboard for badge updates)
        this.overviewModule = new OverviewModule(this.api, this);
        this.queuesModule = new QueuesModule(this.api, this);
        this.workersModule = new WorkersModule(this.api, this);
        this.tasksModule = new TasksModule(this.api, this);
    }

    /**
     * Initialize dashboard
     */
    init() {
        console.log('Initializing Tasks Dashboard...');
        this.setupEventListeners();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = e.currentTarget.dataset.tab;
                this.switchTab(tabId);
            });
        });

        // Management actions
        document.getElementById('simulate-data-btn')?.addEventListener('click', () => this.simulateData());
        document.getElementById('clear-test-data-btn')?.addEventListener('click', () => this.clearData());
        document.getElementById('clear-all-queues-btn')?.addEventListener('click', () => this.clearQueues());
        document.getElementById('purge-failed-tasks-btn')?.addEventListener('click', () => this.purgeFailed());
    }

    /**
     * Switch tabs
     */
    switchTab(tabId) {
        console.log('Switching to tab:', tabId);
        
        // Update active tab styling
        document.querySelectorAll('.tab-button').forEach(tab => {
            tab.classList.remove('active');
            tab.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300', 'dark:text-gray-400', 'dark:hover:text-gray-300');
        });

        // Add active to selected tab
        const activeTab = document.querySelector(`[data-tab="${tabId}"]`);
        if (activeTab) {
            activeTab.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300', 'dark:text-gray-400', 'dark:hover:text-gray-300');
            activeTab.classList.add('active');
        }

        // Hide all tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.add('hidden');
            panel.classList.remove('active');
        });

        // Show selected tab panel
        const activePanel = document.querySelector(`#${tabId}-tab`);
        if (activePanel) {
            activePanel.classList.remove('hidden');
            activePanel.classList.add('active');
        }

        this.currentTab = tabId;
        this.loadTabData(tabId);
    }

    /**
     * Load initial data
     */
    async loadInitialData() {
        console.log('Loading initial data...');
        await this.loadTabData(this.currentTab);
    }

    /**
     * Load data for specific tab using modules
     */
    async loadTabData(tabId) {
        console.log('Loading data for tab:', tabId);
        
        switch (tabId) {
            case 'overview':
                await this.overviewModule.loadData();
                break;
            case 'queues':
                await this.queuesModule.loadData();
                break;
            case 'workers':
                await this.workersModule.loadData();
                break;
            case 'tasks':
                await this.tasksModule.loadData();
                break;
        }
    }

    /**
     * Management actions
     * Using new MJS API with correct method names
     */
    async simulateData() {
        try {
            this.showManagementActionStatus('Simulating test data...', 'info');
            // Using the new API method name from MJS client
            const response = await this.api.tasksApiSimulateCreate({});

            if (response && response.success) {
                this.showManagementActionStatus('Test data simulation completed successfully', 'success');
                await this.loadTabData(this.currentTab);
            } else {
                this.showManagementActionStatus(`Simulation failed: ${response?.error || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            this.showManagementActionStatus(`Simulation error: ${error.message}`, 'error');
        }
    }

    async clearData() {
        try {
            this.showManagementActionStatus('Clearing test data...', 'info');
            // Using the new API method name from MJS client
            const response = await this.api.tasksApiClearCreate({});

            if (response && response.success) {
                this.showManagementActionStatus('Test data cleared successfully', 'success');
                await this.loadTabData(this.currentTab);
            } else {
                this.showManagementActionStatus(`Clear failed: ${response?.error || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            this.showManagementActionStatus(`Clear error: ${error.message}`, 'error');
        }
    }

    async clearQueues() {
        console.log('Clearing queues...');
        this.showManagementActionStatus('Clearing all queues...', 'info');
        try {
            // Using the new API method name from MJS client
            const response = await this.api.tasksApiClearQueuesCreate({});
            if (response && response.success) {
                this.showManagementActionStatus(response.message || 'Queues cleared successfully', 'success');
                this.loadTabData(this.currentTab);
            } else {
                this.showManagementActionStatus(`Failed to clear queues: ${response?.error || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            this.showManagementActionStatus(`Failed to clear queues: ${error.message}`, 'error');
        }
    }

    async purgeFailed() {
        console.log('Purging failed tasks...');
        this.showManagementActionStatus('Purging failed tasks...', 'info');
        try {
            // Using the new API method name from MJS client
            const response = await this.api.tasksApiPurgeFailedCreate({});
            if (response && response.success) {
                this.showManagementActionStatus(response.message || 'Failed tasks purged successfully', 'success');
                this.loadTabData(this.currentTab);
            } else {
                this.showManagementActionStatus(`Failed to purge failed tasks: ${response?.error || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            this.showManagementActionStatus(`Failed to purge failed tasks: ${error.message}`, 'error');
        }
    }

    /**
     * Show management action status
     */
    showManagementActionStatus(message, type = 'info') {
        const statusDiv = document.getElementById('management-action-status');
        const messageSpan = document.getElementById('management-action-message');
        
        if (statusDiv && messageSpan) {
            messageSpan.textContent = message;
            statusDiv.classList.remove('hidden');
            
            setTimeout(() => {
                statusDiv.classList.add('hidden');
            }, 5000);
        }
    }

    /**
     * Update tab badges with counts
     */
    updateTabBadges(data) {
        // Update queues badge
        const queuesBadge = document.querySelector('#queues-count-badge');
        if (queuesBadge && data.active_queues !== undefined) {
            queuesBadge.textContent = data.active_queues;
        }

        // Update workers badge
        const workersBadge = document.querySelector('#workers-count-badge');
        if (workersBadge && data.workers !== undefined) {
            workersBadge.textContent = data.workers;
        }

        // Update tasks badge - will be updated by tasks module
        const tasksBadge = document.querySelector('#tasks-count-badge');
        if (tasksBadge && data.total_tasks !== undefined) {
            tasksBadge.textContent = data.total_tasks;
        }
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            this.loadTabData(this.currentTab);
        }, this.refreshRate);
    }
}

// Wait for both DOM and API to be ready
async function initializeDashboard() {
    console.log('DOM loaded, waiting for TasksAPI...');

    // Wait for API to be available (max 5 seconds)
    let attempts = 0;
    const maxAttempts = 100; // 100 * 50ms = 5 seconds

    while (!window.tasksAPI && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 50));
        attempts++;
    }

    if (!window.tasksAPI) {
        console.error('❌ TasksAPI failed to load after 5 seconds');
        return;
    }

    console.log('✅ TasksAPI ready, initializing dashboard...');
    window.dashboard = new TasksDashboard();
    window.dashboard.init();
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', initializeDashboard);