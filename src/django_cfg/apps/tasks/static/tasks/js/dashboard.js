/**
 * Dashboard Main Logic
 * Handles tab navigation, data loading, and UI updates
 */

class TasksDashboard {
    constructor() {
        this.currentTab = 'overview';
        this.refreshInterval = null;
        this.refreshRate = 30000; // 30 seconds
        
        this.init();
    }

    /**
     * Initialize dashboard
     */
    init() {
        this.setupTabNavigation();
        this.setupEventListeners();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    /**
     * Setup tab navigation
     */
    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabPanels = document.querySelectorAll('.tab-panel');

        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = e.currentTarget.dataset.tab;
                this.switchTab(tabId);
            });
        });
    }

    /**
     * Switch to a specific tab
     * @param {string} tabId - Tab identifier
     */
    switchTab(tabId) {
        // Update button states
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active', 'border-primary-500', 'text-primary-600', 'dark:text-primary-400');
            btn.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300', 'dark:text-gray-400', 'dark:hover:text-gray-300');
        });

        const activeButton = document.querySelector(`[data-tab="${tabId}"]`);
        if (activeButton) {
            activeButton.classList.add('active', 'border-primary-500', 'text-primary-600', 'dark:text-primary-400');
            activeButton.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300', 'dark:text-gray-400', 'dark:hover:text-gray-300');
        }

        // Update panel visibility
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.add('hidden');
            panel.classList.remove('active');
        });

        const activePanel = document.getElementById(`${tabId}-tab`);
        if (activePanel) {
            activePanel.classList.remove('hidden');
            activePanel.classList.add('active');
        }

        this.currentTab = tabId;
        this.loadTabData(tabId);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh buttons
        const refreshQueuesBtn = document.getElementById('refresh-queues-btn');
        if (refreshQueuesBtn) {
            refreshQueuesBtn.addEventListener('click', () => this.loadQueueData());
        }

        const refreshTasksBtn = document.getElementById('refresh-tasks-btn');
        if (refreshTasksBtn) {
            refreshTasksBtn.addEventListener('click', () => this.loadTaskData());
        }

        // Worker management buttons
        const startWorkersBtn = document.getElementById('start-workers-btn');
        if (startWorkersBtn) {
            startWorkersBtn.addEventListener('click', () => this.startWorkers());
        }

        const stopWorkersBtn = document.getElementById('stop-workers-btn');
        if (stopWorkersBtn) {
            stopWorkersBtn.addEventListener('click', () => this.stopWorkers());
        }

        // Queue management buttons
        const clearQueuesBtn = document.getElementById('clear-queues-btn');
        if (clearQueuesBtn) {
            clearQueuesBtn.addEventListener('click', () => this.clearQueues());
        }

        const purgeFailedBtn = document.getElementById('purge-failed-btn');
        if (purgeFailedBtn) {
            purgeFailedBtn.addEventListener('click', () => this.purgeFailedTasks());
        }

        // Task status filter
        const taskStatusFilter = document.getElementById('task-status-filter');
        if (taskStatusFilter) {
            taskStatusFilter.addEventListener('change', () => this.loadTaskData());
        }

        // Management action buttons
        const clearAllQueuesBtn = document.getElementById('clear-all-queues-btn');
        if (clearAllQueuesBtn) {
            clearAllQueuesBtn.addEventListener('click', () => this.clearAllQueues());
        }

        const purgeFailedTasksBtn = document.getElementById('purge-failed-tasks-btn');
        if (purgeFailedTasksBtn) {
            purgeFailedTasksBtn.addEventListener('click', () => this.purgeFailedTasks());
        }
    }

    /**
     * Load initial data
     */
    async loadInitialData() {
        await this.loadOverviewData();
    }

    /**
     * Load data for specific tab
     * @param {string} tabId - Tab identifier
     */
    async loadTabData(tabId) {
        switch (tabId) {
            case 'overview':
                await this.loadOverviewData();
                break;
            case 'queues':
                await this.loadQueueData();
                break;
            case 'workers':
                await this.loadWorkerData();
                break;
            case 'tasks':
                await this.loadTaskData();
                break;
        }
    }

    /**
     * Load overview data
     */
    async loadOverviewData() {
        try {
            const [queueData, taskData] = await Promise.all([
                window.tasksAPI.getQueueStatus(),
                window.tasksAPI.getTaskStatistics()
            ]);
            

            // Extract data from API response wrapper
            const actualQueueData = queueData.data || queueData;
            const actualTaskData = taskData.data || taskData;

            this.updateStatusCards(actualQueueData, actualTaskData);
            this.updateSystemStatus(actualQueueData, actualTaskData);
        } catch (error) {
            console.error('Failed to load overview data:', error);
            this.showError('Failed to load overview data');
        }
    }

    /**
     * Update status cards
     * @param {Object} queueData - Queue status data
     * @param {Object} taskData - Task statistics data
     */
    updateStatusCards(queueData, taskData) {
        // Active queues
        const activeQueuesEl = document.getElementById('active-queues-count');
        if (activeQueuesEl && queueData.queues) {
            const activeQueues = Object.keys(queueData.queues).length;
            activeQueuesEl.textContent = activeQueues;
        }

        // Active workers
        const activeWorkersEl = document.getElementById('active-workers-count');
        if (activeWorkersEl && queueData.workers) {
            activeWorkersEl.textContent = queueData.workers.length || 0;
        }

        // Pending tasks
        const pendingTasksEl = document.getElementById('pending-tasks-count');
        if (pendingTasksEl && queueData.queues) {
            const pendingTasks = Object.values(queueData.queues).reduce((sum, queue) => sum + (queue.size || 0), 0);
            pendingTasksEl.textContent = pendingTasks;
        }

        // Failed tasks
        const failedTasksEl = document.getElementById('failed-tasks-count');
        if (failedTasksEl && taskData.statistics) {
            failedTasksEl.textContent = taskData.statistics.failed || 0;
        }
    }

    /**
     * Update system status
     * @param {Object} queueData - Queue status data
     * @param {Object} taskData - Task statistics data
     */
    updateSystemStatus(queueData, taskData) {
        const container = document.getElementById('system-status-container');
        if (!container) return;

        // System is healthy if Redis is connected, workers are optional in development
        const isHealthy = queueData.redis_connected;
        
        container.innerHTML = `
            <div class="space-y-4">
                <div class="flex items-center justify-between p-4 rounded-lg ${isHealthy ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'}">
                    <div class="flex items-center">
                        <span class="material-icons text-2xl mr-3 ${isHealthy ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}">
                            ${isHealthy ? 'check_circle' : 'error'}
                        </span>
                        <div>
                            <h3 class="font-medium ${isHealthy ? 'text-green-900 dark:text-green-100' : 'text-red-900 dark:text-red-100'}">
                                System ${isHealthy ? 'Healthy' : 'Issues Detected'}
                            </h3>
                            <p class="text-sm ${isHealthy ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'}">
                                ${isHealthy ? 'All systems operational' : 'Some components need attention'}
                            </p>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-sm text-gray-500 dark:text-gray-400">
                            Last updated: ${new Date().toLocaleTimeString()}
                        </div>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="flex items-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                        <span class="material-icons text-lg mr-2 ${queueData.redis_connected ? 'text-green-600' : 'text-red-600'}">
                            ${queueData.redis_connected ? 'check' : 'close'}
                        </span>
                        <span class="text-sm">Redis: ${queueData.redis_connected ? 'Connected' : 'Disconnected'}</span>
                    </div>
                    
                    <div class="flex items-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                        <span class="material-icons text-lg mr-2 ${queueData.workers && queueData.workers.length > 0 ? 'text-green-600' : 'text-red-600'}">
                            ${queueData.workers && queueData.workers.length > 0 ? 'check' : 'close'}
                        </span>
                        <span class="text-sm">Workers: ${queueData.workers ? queueData.workers.length : 0} active</span>
                    </div>
                    
                    <div class="flex items-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                        <span class="material-icons text-lg mr-2 text-blue-600">
                            queue
                        </span>
                        <span class="text-sm">Queues: ${queueData.queues ? Object.keys(queueData.queues).length : 0} configured</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Load queue data
     */
    async loadQueueData() {
        try {
            const response = await window.tasksAPI.getQueueStatus();
            const data = response.data || response;
            this.updateQueuesContainer(data);
        } catch (error) {
            console.error('Failed to load queue data:', error);
            this.showError('Failed to load queue data');
        }
    }

    /**
     * Update queues container
     * @param {Object} data - Queue data
     */
    updateQueuesContainer(data) {
        const container = document.getElementById('queues-container');
        if (!container || !data.queues) return;

        const queuesHtml = Object.entries(data.queues).map(([name, queue]) => `
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="font-medium text-gray-900 dark:text-white">${name}</h3>
                    <span class="px-2 py-1 text-xs rounded-full ${queue.size > 0 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'}">
                        ${queue.size || 0} tasks
                    </span>
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">
                    <p>Size: ${queue.size || 0}</p>
                    <p>Status: ${queue.size > 0 ? 'Active' : 'Empty'}</p>
                </div>
            </div>
        `).join('');

        container.innerHTML = queuesHtml || '<p class="text-gray-500 dark:text-gray-400">No queues configured</p>';
    }

    /**
     * Load worker data
     */
    async loadWorkerData() {
        try {
            const response = await window.tasksAPI.getQueueStatus();
            const data = response.data || response;
            this.updateWorkersContainer(data);
        } catch (error) {
            console.error('Failed to load worker data:', error);
            this.showError('Failed to load worker data');
        }
    }

    /**
     * Update workers container
     * @param {Object} data - Worker data
     */
    updateWorkersContainer(data) {
        const container = document.getElementById('workers-container');
        if (!container) return;

        if (data.workers && data.workers.length > 0) {
            const workersHtml = data.workers.map(worker => `
                <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="font-medium text-gray-900 dark:text-white">Worker ${worker.id || 'Unknown'}</h3>
                            <p class="text-sm text-gray-600 dark:text-gray-400">Status: ${worker.status || 'Active'}</p>
                        </div>
                        <span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            Running
                        </span>
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = workersHtml;
        } else {
            container.innerHTML = '<p class="text-gray-500 dark:text-gray-400">No active workers</p>';
        }
    }

    /**
     * Load task data
     */
    async loadTaskData() {
        try {
            const response = await window.tasksAPI.getTaskStatistics();
            const data = response.data || response;
            this.updateTasksContainer(data);
        } catch (error) {
            console.error('Failed to load task data:', error);
            this.showError('Failed to load task data');
        }
    }

    /**
     * Update tasks container
     * @param {Object} data - Task data
     */
    updateTasksContainer(data) {
        const container = document.getElementById('tasks-container');
        if (!container) return;

        if (data.recent_tasks && data.recent_tasks.length > 0) {
            const tasksHtml = data.recent_tasks.map(task => `
                <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="font-medium text-gray-900 dark:text-white">${task.actor_name || 'Unknown Task'}</h3>
                            <p class="text-sm text-gray-600 dark:text-gray-400">
                                Created: ${new Date(task.created_at).toLocaleString()}
                            </p>
                        </div>
                        <span class="px-2 py-1 text-xs rounded-full ${this.getStatusColor(task.status)}">
                            ${task.status || 'Unknown'}
                        </span>
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = tasksHtml;
        } else {
            container.innerHTML = '<p class="text-gray-500 dark:text-gray-400">No recent tasks</p>';
        }
    }

    /**
     * Get status color classes
     * @param {string} status - Task status
     * @returns {string} CSS classes
     */
    getStatusColor(status) {
        switch (status) {
            case 'done':
                return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
            case 'failed':
                return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
            case 'running':
                return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
            case 'pending':
                return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
            default:
                return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
        }
    }

    /**
     * Start workers
     */
    async startWorkers() {
        try {
            const processes = document.getElementById('worker-processes')?.value || 1;
            const threads = document.getElementById('worker-threads')?.value || 4;
            
            await window.tasksAPI.startWorkers({ processes, threads });
            this.showSuccess('Workers started successfully');
            this.loadTabData(this.currentTab);
        } catch (error) {
            console.error('Failed to start workers:', error);
            this.showError('Failed to start workers');
        }
    }

    /**
     * Stop workers
     */
    async stopWorkers() {
        try {
            await window.tasksAPI.stopWorkers();
            this.showSuccess('Workers stopped successfully');
            this.loadTabData(this.currentTab);
        } catch (error) {
            console.error('Failed to stop workers:', error);
            this.showError('Failed to stop workers');
        }
    }

    /**
     * Clear all queues
     */
    async clearQueues() {
        if (!confirm('Are you sure you want to clear all queues? This will remove all pending tasks.')) {
            return;
        }

        try {
            await window.tasksAPI.clearQueues();
            this.showSuccess('Queues cleared successfully');
            this.loadTabData(this.currentTab);
        } catch (error) {
            console.error('Failed to clear queues:', error);
            this.showError('Failed to clear queues');
        }
    }

    /**
     * Clear all queues (from management actions)
     */
    async clearAllQueues() {
        if (!confirm('Are you sure you want to clear all queues? This will remove all pending tasks.')) {
            return;
        }

        try {
            this.showManagementActionStatus('Clearing all queues...', 'info');
            await window.tasksAPI.clearQueues();
            this.showManagementActionStatus('✅ All queues cleared successfully', 'success');
            this.loadTabData(this.currentTab);
        } catch (error) {
            console.error('Failed to clear queues:', error);
            this.showManagementActionStatus('❌ Failed to clear queues', 'error');
        }
    }

    /**
     * Purge failed tasks
     */
    async purgeFailedTasks() {
        if (!confirm('Are you sure you want to purge all failed tasks?')) {
            return;
        }

        try {
            // Check if called from management actions
            const isFromManagementActions = event && event.target && event.target.id === 'purge-failed-tasks-btn';
            
            if (isFromManagementActions) {
                this.showManagementActionStatus('Purging failed tasks...', 'info');
            }
            
            await window.tasksAPI.purgeFailedTasks();
            
            if (isFromManagementActions) {
                this.showManagementActionStatus('✅ Failed tasks purged successfully', 'success');
            } else {
                this.showSuccess('Failed tasks purged successfully');
            }
            
            this.loadTabData(this.currentTab);
        } catch (error) {
            console.error('Failed to purge failed tasks:', error);
            
            const isFromManagementActions = event && event.target && event.target.id === 'purge-failed-tasks-btn';
            if (isFromManagementActions) {
                this.showManagementActionStatus('❌ Failed to purge failed tasks', 'error');
            } else {
                this.showError('Failed to purge failed tasks');
            }
        }
    }

    /**
     * Start auto refresh
     */
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadTabData(this.currentTab);
        }, this.refreshRate);
    }

    /**
     * Stop auto refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * Show success message
     * @param {string} message - Success message
     */
    showSuccess(message) {
        // Simple implementation - can be enhanced with toast notifications
        console.log('Success:', message);
        alert(message);
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        // Simple implementation - can be enhanced with toast notifications
        console.error('Error:', message);
        alert(`Error: ${message}`);
    }

    /**
     * Show management action status
     * @param {string} message - Status message
     * @param {string} type - Status type (info, success, error)
     */
    showManagementActionStatus(message, type = 'info') {
        const statusContainer = document.getElementById('management-action-status');
        const messageElement = document.getElementById('management-action-message');
        
        if (!statusContainer || !messageElement) {
            return;
        }

        // Update message
        messageElement.textContent = message;
        
        // Update styling based on type
        statusContainer.className = 'mt-4';
        const statusDiv = statusContainer.querySelector('div');
        
        if (type === 'success') {
            statusDiv.className = 'p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800';
            statusDiv.querySelector('.material-icons').className = 'material-icons text-green-600 dark:text-green-400 mr-2';
            messageElement.className = 'text-sm text-green-800 dark:text-green-200';
        } else if (type === 'error') {
            statusDiv.className = 'p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800';
            statusDiv.querySelector('.material-icons').className = 'material-icons text-red-600 dark:text-red-400 mr-2';
            messageElement.className = 'text-sm text-red-800 dark:text-red-200';
        } else {
            statusDiv.className = 'p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800';
            statusDiv.querySelector('.material-icons').className = 'material-icons text-blue-600 dark:text-blue-400 mr-2';
            messageElement.className = 'text-sm text-blue-800 dark:text-blue-200';
        }
        
        // Show status
        statusContainer.classList.remove('hidden');
        
        // Auto-hide after 5 seconds for success/error messages
        if (type === 'success' || type === 'error') {
            setTimeout(() => {
                statusContainer.classList.add('hidden');
            }, 5000);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new TasksDashboard();
});
