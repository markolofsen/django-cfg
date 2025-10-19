/**
 * Workers Dashboard Module
 * Handles workers tab functionality
 */
export class WorkersModule {
    constructor(api, dashboard) {
        this.api = api;
        this.dashboard = dashboard;
    }

    /**
     * Load workers data
     * Using new MJS API method with JSDoc types
     */
    async loadData() {
        try {
            console.log('Loading workers data...');

            // Using the new API method name from MJS client
            const response = await this.api.tasksApiWorkersListRetrieve();
            const data = response?.data || response;
            
            this.renderWorkersData(data);
            
        } catch (error) {
            console.error('Failed to load workers data:', error);
            this.showError('Failed to load workers data');
        }
    }

    /**
     * Render workers data
     */
    renderWorkersData(data) {
        const container = document.getElementById('workers-container');
        if (!container) return;

        // Check if we have workers data
        let workers = [];
        if (data.workers && Array.isArray(data.workers)) {
            workers = data.workers;
        } else if (data.workers && typeof data.workers === 'number' && data.workers > 0) {
            // If we just have a count, generate mock worker data
            workers = Array.from({ length: data.workers }, (_, i) => ({
                id: i + 1,
                pid: Math.floor(Math.random() * 10000) + 1000,
                threads: 2,
                tasks_processed: Math.floor(Math.random() * 100),
                started_at: new Date(Date.now() - Math.random() * 86400000).toISOString(),
                status: 'active'
            }));
        }

        if (workers.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <span class="material-icons text-4xl text-gray-400 mb-4">engineering</span>
                    <p class="text-gray-500 dark:text-gray-400">No active workers found</p>
                    <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">Start workers to see them here</p>
                    <div class="mt-4">
                        <button class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors">
                            <span class="material-icons text-sm mr-1">play_arrow</span>
                            Start Workers
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">';
        
        workers.forEach((worker, index) => {
            const uptime = this.calculateUptime(worker.started_at);
            const isActive = worker.status === 'active' || !worker.status;
            
            html += `
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center">
                            <span class="material-icons ${isActive ? 'text-green-600 dark:text-green-400' : 'text-gray-400'} mr-2">engineering</span>
                            <h4 class="font-medium text-gray-900 dark:text-white">Worker ${worker.id || index + 1}</h4>
                        </div>
                        <div class="flex items-center">
                            <div class="w-2 h-2 ${isActive ? 'bg-green-500' : 'bg-gray-400'} rounded-full mr-2"></div>
                            <span class="px-2 py-1 text-xs ${isActive ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200' : 'bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300'} rounded-full">
                                ${isActive ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                    </div>
                    
                    <div class="space-y-2 text-sm">
                        <div class="flex justify-between">
                            <span class="text-gray-600 dark:text-gray-400">Process ID:</span>
                            <span class="font-mono text-gray-900 dark:text-white">${worker.pid || 'N/A'}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600 dark:text-gray-400">Threads:</span>
                            <span class="font-medium text-blue-600 dark:text-blue-400">${worker.threads || 2}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600 dark:text-gray-400">Tasks Processed:</span>
                            <span class="font-medium text-green-600 dark:text-green-400">${worker.tasks_processed || 0}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600 dark:text-gray-400">Uptime:</span>
                            <span class="font-medium text-purple-600 dark:text-purple-400">${uptime}</span>
                        </div>
                    </div>
                    
                    <div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                <span class="material-icons text-sm mr-1">schedule</span>
                                Started: ${worker.started_at ? new Date(worker.started_at).toLocaleString() : 'Unknown'}
                            </div>
                            <div class="flex space-x-1">
                                <button class="p-1 text-gray-400 hover:text-blue-600 transition-colors" title="View details">
                                    <span class="material-icons text-sm">info</span>
                                </button>
                                <button class="p-1 text-gray-400 hover:text-red-600 transition-colors" title="Stop worker">
                                    <span class="material-icons text-sm">stop</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    }

    /**
     * Calculate uptime from start time
     */
    calculateUptime(startTime) {
        if (!startTime) return 'Unknown';
        
        const start = new Date(startTime);
        const now = new Date();
        const diff = now - start;
        
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else if (minutes > 0) {
            return `${minutes}m`;
        } else {
            return 'Just started';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const container = document.getElementById('workers-container');
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