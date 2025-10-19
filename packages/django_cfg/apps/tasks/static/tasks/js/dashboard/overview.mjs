/**
 * Overview Dashboard Module
 * Handles overview tab functionality
 */
export class OverviewModule {
    constructor(api, dashboard) {
        this.api = api;
        this.dashboard = dashboard; // Reference to main dashboard for badge updates
    }

    /**
     * Load overview data
     * Using new MJS API methods with JSDoc types
     */
    async loadData() {
        try {
            console.log('Loading overview data...');

            // Using the new API method names from MJS client
            const [queueData, taskStats] = await Promise.all([
                this.api.tasksApiQueuesStatusRetrieve(),
                this.api.tasksApiTasksStatsRetrieve()
            ]);

            const queueInfo = queueData?.data || queueData;
            const taskInfo = taskStats?.data || taskStats;

            this.updateStatusCards(queueInfo, taskInfo);
            this.updateSystemStatus(queueInfo);
            
            // Update tab badges
            if (this.dashboard && this.dashboard.updateTabBadges) {
                this.dashboard.updateTabBadges(queueInfo);
            }
            
        } catch (error) {
            console.error('Failed to load overview data:', error);
            this.showError('Failed to load overview data');
        }
    }

    /**
     * Update status cards
     */
    updateStatusCards(queueData, taskData) {
        this.updateElement('active-queues-count', queueData.active_queues || 0);
        this.updateElement('workers-count', queueData.workers || 0);
        this.updateElement('pending-tasks-count', queueData.total_pending || 0);
        this.updateElement('failed-tasks-count', queueData.total_failed || 0);
    }

    /**
     * Update system status
     */
    updateSystemStatus(data) {
        const statusContainer = document.getElementById('system-status');
        if (!statusContainer) return;

        const isHealthy = data.redis_connected && !data.error;
        const timestamp = new Date().toLocaleTimeString();

        statusContainer.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center">
                    <span class="material-icons text-2xl mr-3 ${isHealthy ? 'text-green-600' : 'text-red-600'}">
                        ${isHealthy ? 'check_circle' : 'error'}
                    </span>
                    <div>
                        <h3 class="text-lg font-semibold ${isHealthy ? 'text-green-800' : 'text-red-800'} dark:${isHealthy ? 'text-green-200' : 'text-red-200'}">
                            ${isHealthy ? 'System Healthy' : 'System Issues Detected'}
                        </h3>
                        <p class="text-sm text-gray-600 dark:text-gray-400">
                            ${isHealthy ? 'All systems operational' : 'Some components need attention'}
                        </p>
                    </div>
                </div>
                <span class="text-xs text-gray-500 dark:text-gray-400">Last updated: ${timestamp}</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div class="flex items-center">
                    <span class="material-icons text-base mr-2 ${data.redis_connected ? 'text-green-500' : 'text-red-500'}">
                        ${data.redis_connected ? 'check' : 'close'}
                    </span>
                    <span class="text-gray-700 dark:text-gray-300">Redis: ${data.redis_connected ? 'Connected' : 'Disconnected'}</span>
                </div>
                <div class="flex items-center">
                    <span class="material-icons text-base mr-2 ${data.workers > 0 ? 'text-green-500' : 'text-red-500'}">
                        ${data.workers > 0 ? 'check' : 'close'}
                    </span>
                    <span class="text-gray-700 dark:text-gray-300">Workers: ${data.workers} active</span>
                </div>
                <div class="flex items-center">
                    <span class="material-icons text-base mr-2 ${data.active_queues > 0 ? 'text-blue-500' : 'text-gray-500'}">queue</span>
                    <span class="text-gray-700 dark:text-gray-300">Queues: ${data.active_queues || 0} configured</span>
                </div>
            </div>
        `;
    }

    /**
     * Helper method to update element text
     */
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error(message);
        const statusContainer = document.getElementById('system-status');
        if (statusContainer) {
            statusContainer.innerHTML = `
                <div class="text-center py-8">
                    <span class="material-icons text-4xl text-red-400 mb-4">error</span>
                    <p class="text-red-600 dark:text-red-400">${message}</p>
                </div>
            `;
        }
    }
}