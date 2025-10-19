/**
 * Queues Dashboard Module
 * Handles queues tab functionality
 */
export class QueuesModule {
    constructor(api, dashboard) {
        this.api = api;
        this.dashboard = dashboard;
    }

    /**
     * Load queues data
     * Using new MJS API method with JSDoc types
     */
    async loadData() {
        try {
            console.log('Loading queues data...');

            // Using the new API method name from MJS client
            const response = await this.api.tasksApiQueuesStatusRetrieve();
            const data = response?.data || response;
            
            this.renderQueuesData(data);
            
        } catch (error) {
            console.error('Failed to load queues data:', error);
            this.showError('Failed to load queues data');
        }
    }

    /**
     * Render queues data
     */
    renderQueuesData(data) {
        const container = document.getElementById('queues-container');
        if (!container) return;

        if (!data.queues || Object.keys(data.queues).length === 0) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <span class="material-icons text-4xl text-gray-400 mb-4">queue</span>
                    <p class="text-gray-500 dark:text-gray-400">No active queues found</p>
                    <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">Queues will appear here when tasks are processed</p>
                </div>
            `;
            return;
        }

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">';
        
        Object.entries(data.queues).forEach(([queueName, queueInfo]) => {
            const totalTasks = (queueInfo.pending || 0) + (queueInfo.failed || 0) + (queueInfo.processed || 0);
            
            html += `
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center">
                            <span class="material-icons text-blue-600 dark:text-blue-400 mr-2">queue</span>
                            <h4 class="font-medium text-gray-900 dark:text-white">${queueName}</h4>
                        </div>
                        <span class="px-2 py-1 text-xs ${totalTasks > 0 ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200' : 'bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300'} rounded-full">
                            ${totalTasks > 0 ? 'Active' : 'Idle'}
                        </span>
                    </div>
                    
                    <div class="space-y-2 text-sm">
                        <div class="flex justify-between">
                            <span class="text-gray-600 dark:text-gray-400">Pending:</span>
                            <span class="font-medium text-yellow-600 dark:text-yellow-400">${queueInfo.pending || 0}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600 dark:text-gray-400">Failed:</span>
                            <span class="font-medium text-red-600 dark:text-red-400">${queueInfo.failed || 0}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600 dark:text-gray-400">Processed:</span>
                            <span class="font-medium text-green-600 dark:text-green-400">${queueInfo.processed || 0}</span>
                        </div>
                    </div>
                    
                    ${totalTasks > 0 ? `
                        <div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                            <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                                <div class="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full transition-all duration-300" 
                                     style="width: ${Math.min(100, (queueInfo.processed || 0) / totalTasks * 100)}%"></div>
                            </div>
                            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                                <span>Progress</span>
                                <span>${Math.round((queueInfo.processed || 0) / totalTasks * 100)}%</span>
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                        <div class="flex items-center text-xs text-gray-500 dark:text-gray-400">
                            <span class="material-icons text-sm mr-1">schedule</span>
                            Last activity: ${queueInfo.last_activity ? new Date(queueInfo.last_activity).toLocaleTimeString() : 'Never'}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    }

    /**
     * Show error message
     */
    showError(message) {
        const container = document.getElementById('queues-container');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <span class="material-icons text-4xl text-red-400 mb-4">error</span>
                    <p class="text-red-600 dark:text-red-400">${message}</p>
                </div>
            `;
        }
    }
}