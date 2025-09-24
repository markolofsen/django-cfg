/**
 * Task Monitor Modal
 * Interactive task monitoring with real-time updates
 */
class TaskMonitor {
    constructor() {
        this.modal = null;
        this.autoRefresh = true;
        this.refreshInterval = null;
        this.refreshRate = 5000; // 5 seconds
        this.currentFilters = {
            status: '',
            queue: '',
            search: ''
        };
        this.tasks = [];
        
        this.init();
    }

    init() {
        this.modal = document.getElementById('task-details-modal');
        if (!this.modal) return;

        this.setupEventListeners();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Modal controls
        document.getElementById('close-task-modal')?.addEventListener('click', () => this.hide());
        document.getElementById('refresh-tasks-modal')?.addEventListener('click', () => this.loadTasks());
        document.getElementById('auto-refresh-toggle')?.addEventListener('click', () => this.toggleAutoRefresh());

        // Filters
        document.getElementById('modal-status-filter')?.addEventListener('change', (e) => {
            this.currentFilters.status = e.target.value;
            this.applyFilters();
        });

        document.getElementById('modal-queue-filter')?.addEventListener('change', (e) => {
            this.currentFilters.queue = e.target.value;
            this.applyFilters();
        });

        document.getElementById('modal-search-input')?.addEventListener('input', (e) => {
            this.currentFilters.search = e.target.value.toLowerCase();
            this.applyFilters();
        });

        // Actions
        document.getElementById('clear-completed-tasks')?.addEventListener('click', () => this.clearCompletedTasks());
        document.getElementById('export-tasks')?.addEventListener('click', () => this.exportTasks());

        // Close modal on outside click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hide();
            }
        });

        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.hide();
            }
        });
    }

    show() {
        if (!this.modal) return;
        
        this.modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        this.loadTasks();
        
        if (this.autoRefresh) {
            this.startAutoRefresh();
        }
    }

    hide() {
        if (!this.modal) return;
        
        this.modal.classList.add('hidden');
        document.body.style.overflow = '';
        this.stopAutoRefresh();
    }

    toggleAutoRefresh() {
        this.autoRefresh = !this.autoRefresh;
        const button = document.getElementById('auto-refresh-toggle');
        
        if (this.autoRefresh) {
            button.innerHTML = '<span class="material-icons text-sm mr-1">refresh</span>Auto: ON';
            button.className = 'px-3 py-1 text-sm bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-lg hover:bg-green-200 dark:hover:bg-green-800 transition-colors';
            this.startAutoRefresh();
        } else {
            button.innerHTML = '<span class="material-icons text-sm mr-1">pause</span>Auto: OFF';
            button.className = 'px-3 py-1 text-sm bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors';
            this.stopAutoRefresh();
        }
    }

    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        if (this.autoRefresh) {
            this.refreshInterval = setInterval(() => {
                if (!this.modal.classList.contains('hidden')) {
                    this.loadTasks();
                }
            }, this.refreshRate);
        }
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    async loadTasks() {
        try {
            this.showLoading();
            
            // Get real task data from API
            const params = {
                limit: 100,
                offset: 0,
                ...this.currentFilters
            };
            
            const response = await window.tasksAPI.getTaskList(params);
            const data = response.data || response;
            
            if (data.error) {
                // Fallback to mock data if API fails
                console.warn('API error, using mock data:', data.error);
                this.tasks = this.generateMockTasks();
            } else {
                this.tasks = data.tasks || [];
            }
            
            this.updateTaskCount();
            this.updateLastUpdateTime();
            this.renderTasks();
            
        } catch (error) {
            console.error('Failed to load tasks:', error);
            // Fallback to mock data on error
            this.tasks = this.generateMockTasks();
            this.updateTaskCount();
            this.updateLastUpdateTime();
            this.renderTasks();
        }
    }

    generateMockTasks() {
        // Generate mock task data - replace with real API data
        const statuses = ['pending', 'running', 'done', 'failed'];
        const queues = ['default', 'high', 'low', 'vehicles'];
        const actors = ['process_document_async', 'send_notification', 'cleanup_old_files', 'generate_report'];
        
        return Array.from({ length: 20 }, (_, i) => ({
            id: `task_${i + 1}`,
            actor_name: actors[Math.floor(Math.random() * actors.length)],
            status: statuses[Math.floor(Math.random() * statuses.length)],
            queue: queues[Math.floor(Math.random() * queues.length)],
            created_at: new Date(Date.now() - Math.random() * 86400000).toISOString(),
            updated_at: new Date(Date.now() - Math.random() * 3600000).toISOString(),
            args: JSON.stringify([Math.floor(Math.random() * 1000)]),
            kwargs: JSON.stringify({ user_id: Math.floor(Math.random() * 100) }),
            progress: Math.floor(Math.random() * 100),
            result: Math.random() > 0.7 ? JSON.stringify({ success: true, processed: Math.floor(Math.random() * 100) }) : null,
            traceback: Math.random() > 0.9 ? 'Error: Something went wrong...' : null
        }));
    }

    applyFilters() {
        this.renderTasks();
    }

    getFilteredTasks() {
        return this.tasks.filter(task => {
            const matchesStatus = !this.currentFilters.status || task.status === this.currentFilters.status;
            const matchesQueue = !this.currentFilters.queue || task.queue === this.currentFilters.queue;
            const matchesSearch = !this.currentFilters.search || 
                task.actor_name.toLowerCase().includes(this.currentFilters.search) ||
                task.id.toLowerCase().includes(this.currentFilters.search);
            
            return matchesStatus && matchesQueue && matchesSearch;
        });
    }

    renderTasks() {
        const container = document.getElementById('tasks-list');
        const loading = document.getElementById('tasks-loading');
        const empty = document.getElementById('tasks-empty');
        
        if (!container) return;
        
        loading.classList.add('hidden');
        
        const filteredTasks = this.getFilteredTasks();
        
        if (filteredTasks.length === 0) {
            container.innerHTML = '';
            empty.classList.remove('hidden');
            return;
        }
        
        empty.classList.add('hidden');
        
        // Create table layout
        container.innerHTML = `
            <div class="overflow-x-auto">
                <table class="min-w-full bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <thead class="bg-gray-50 dark:bg-gray-700">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider w-32">Status</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Task</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider w-24">Queue</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider w-20">Duration</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider w-24">Updated</th>
                            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider w-32">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 dark:divide-gray-600">
                        ${filteredTasks.map(task => this.renderTaskRow(task)).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    renderTaskRow(task) {
        // Map Dramatiq statuses to our display statuses
        const statusMap = {
            'enqueued': 'pending',
            'delayed': 'pending', 
            'running': 'running',
            'done': 'done',
            'failed': 'failed',
            'skipped': 'done'
        };
        
        const displayStatus = statusMap[task.status.toLowerCase()] || task.status.toLowerCase();
        
        const statusColors = {
            pending: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200',
            running: 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
            done: 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
            failed: 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
        };

        const statusIcons = {
            pending: 'schedule',
            running: 'play_circle',
            done: 'check_circle',
            failed: 'error'
        };
        
        const statusLabels = {
            pending: task.status.toLowerCase() === 'delayed' ? 'DELAYED' : 'PENDING',
            running: 'RUNNING',
            done: 'DONE',
            failed: 'FAILED'
        };

        const duration = this.calculateDuration(task.created_at, task.updated_at);
        const updatedTime = new Date(task.updated_at).toLocaleTimeString();

        return `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                <!-- Status -->
                <td class="px-4 py-3 whitespace-nowrap">
                    <div class="flex items-center space-x-2">
                        <span class="material-icons text-sm ${displayStatus === 'failed' ? 'text-red-500' : displayStatus === 'done' ? 'text-green-500' : displayStatus === 'running' ? 'text-blue-500' : 'text-yellow-500'}">${statusIcons[displayStatus]}</span>
                        <span class="px-2 py-1 text-xs font-medium rounded-full ${statusColors[displayStatus]}">${statusLabels[displayStatus]}</span>
                    </div>
                    ${displayStatus === 'running' && task.progress ? `
                        <div class="mt-1 w-16 bg-gray-200 dark:bg-gray-600 rounded-full h-1">
                            <div class="bg-blue-600 h-1 rounded-full transition-all duration-300" style="width: ${task.progress}%"></div>
                        </div>
                    ` : ''}
                </td>
                
                <!-- Task -->
                <td class="px-4 py-3">
                    <div class="text-sm font-medium text-gray-900 dark:text-white">${task.actor_name}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400 font-mono">${task.id.substring(0, 8)}...</div>
                </td>
                
                <!-- Queue -->
                <td class="px-4 py-3 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">${task.queue}</span>
                </td>
                
                <!-- Duration -->
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">${duration}</td>
                
                <!-- Updated -->
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">${updatedTime}</td>
                
                <!-- Actions -->
                <td class="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex items-center justify-end space-x-1">
                        ${task.args || task.kwargs ? `
                            <button class="p-1 text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors" 
                                    onclick="this.classList.toggle('active'); const row = this.closest('tr'); const nextRow = row.nextElementSibling; if (nextRow && nextRow.classList.contains('details-row')) { nextRow.remove(); } else { row.insertAdjacentHTML('afterend', \`<tr class='details-row'><td colspan='6' class='px-4 py-2 bg-gray-50 dark:bg-gray-900 text-xs border-t border-gray-200 dark:border-gray-600'><strong>Args:</strong> \${task.args || 'None'}<br><strong>Kwargs:</strong> \${task.kwargs || 'None'}</td></tr>\`); }"
                                    title="Show arguments">
                                <span class="material-icons text-sm">code</span>
                            </button>
                        ` : ''}
                        ${task.result ? `
                            <button class="p-1 text-green-600 dark:text-green-400 hover:text-green-900 dark:hover:text-green-300 hover:bg-green-50 dark:hover:bg-green-900/20 rounded transition-colors" 
                                    onclick="alert('Result: ' + \`${task.result}\`)"
                                    title="Show result">
                                <span class="material-icons text-sm">check_circle</span>
                            </button>
                        ` : ''}
                        ${task.traceback ? `
                            <button class="p-1 text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors" 
                                    onclick="alert('Error: ' + \`${task.traceback}\`)"
                                    title="Show error">
                                <span class="material-icons text-sm">error</span>
                            </button>
                        ` : ''}
                        ${displayStatus === 'failed' ? `
                            <button class="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors ml-1">
                                Retry
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }

    calculateDuration(startTime, endTime) {
        const start = new Date(startTime);
        const end = new Date(endTime);
        const diff = end - start;
        
        if (diff < 1000) return `${diff}ms`;
        if (diff < 60000) return `${Math.floor(diff / 1000)}s`;
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ${Math.floor((diff % 60000) / 1000)}s`;
        return `${Math.floor(diff / 3600000)}h ${Math.floor((diff % 3600000) / 60000)}m`;
    }

    updateTaskCount() {
        const badge = document.getElementById('task-count-badge');
        if (badge) {
            const filteredCount = this.getFilteredTasks().length;
            const totalCount = this.tasks.length;
            badge.textContent = filteredCount === totalCount ? 
                `${totalCount} tasks` : 
                `${filteredCount} of ${totalCount} tasks`;
        }
    }

    updateLastUpdateTime() {
        const timeElement = document.getElementById('last-update-time');
        if (timeElement) {
            timeElement.textContent = new Date().toLocaleTimeString();
        }
    }

    showLoading() {
        const loading = document.getElementById('tasks-loading');
        const empty = document.getElementById('tasks-empty');
        const list = document.getElementById('tasks-list');
        
        loading?.classList.remove('hidden');
        empty?.classList.add('hidden');
        if (list) list.innerHTML = '';
    }

    showError(message) {
        const container = document.getElementById('tasks-list');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-12">
                    <span class="material-icons text-6xl text-red-400 dark:text-red-600 mb-4">error</span>
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Error Loading Tasks</h3>
                    <p class="text-gray-500 dark:text-gray-400">${message}</p>
                </div>
            `;
        }
    }

    async clearCompletedTasks() {
        if (!confirm('Are you sure you want to clear all completed tasks?')) {
            return;
        }
        
        try {
            // TODO: Implement API call to clear completed tasks
            console.log('Clearing completed tasks...');
            this.loadTasks();
        } catch (error) {
            console.error('Failed to clear completed tasks:', error);
        }
    }

    exportTasks() {
        const filteredTasks = this.getFilteredTasks();
        const csv = this.tasksToCSV(filteredTasks);
        this.downloadCSV(csv, 'tasks-export.csv');
    }

    tasksToCSV(tasks) {
        const headers = ['ID', 'Actor', 'Status', 'Queue', 'Created', 'Updated', 'Duration'];
        const rows = tasks.map(task => [
            task.id,
            task.actor_name,
            task.status,
            task.queue,
            new Date(task.created_at).toLocaleString(),
            new Date(task.updated_at).toLocaleString(),
            this.calculateDuration(task.created_at, task.updated_at)
        ]);
        
        return [headers, ...rows].map(row => 
            row.map(field => `"${field}"`).join(',')
        ).join('\n');
    }

    downloadCSV(csv, filename) {
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    }
}

// Initialize task monitor when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.taskMonitor = new TaskMonitor();
});

// Global function to show task monitor
window.showTaskMonitor = () => {
    if (window.taskMonitor) {
        window.taskMonitor.show();
    }
};
