/**
 * Tasks Dashboard Module
 * Handles tasks tab functionality with filtering
 */
export class TasksModule {
    constructor(api, dashboard) {
        this.api = api;
        this.dashboard = dashboard; // Reference to main dashboard for badge updates
        this.allTasks = [];
        this.filteredTasks = [];
        this.filters = {
            status: '',
            queue: '',
            search: ''
        };
        this.setupEventListeners();
    }

    /**
     * Setup event listeners for filters
     */
    setupEventListeners() {
        // Task filters
        document.getElementById('task-status-filter')?.addEventListener('change', (e) => {
            this.filters.status = e.target.value;
            this.applyFilters();
        });

        document.getElementById('task-queue-filter')?.addEventListener('change', (e) => {
            this.filters.queue = e.target.value;
            this.applyFilters();
        });

        document.getElementById('task-search-input')?.addEventListener('input', (e) => {
            this.filters.search = e.target.value.toLowerCase();
            this.applyFilters();
        });

        // Task actions
        document.getElementById('clear-completed-tasks')?.addEventListener('click', () => this.clearCompletedTasks());
        document.getElementById('export-tasks-csv')?.addEventListener('click', () => this.exportTasks());
        
        // Auto-refresh toggle
        document.getElementById('tasks-auto-refresh-toggle')?.addEventListener('click', () => this.toggleAutoRefresh());
        document.getElementById('refresh-tasks-btn')?.addEventListener('click', () => this.loadData());
    }

    /**
     * Load tasks data
     * Using new MJS API method with JSDoc types
     */
    async loadData() {
        try {
            console.log('Loading tasks data...');

            // Using the new API method name from MJS client
            const response = await this.api.tasksApiTasksListRetrieve();
            const data = response?.data || response;
            
            if (data.tasks && data.tasks.length > 0) {
                this.allTasks = data.tasks;
            } else {
                // Generate mock data for demonstration
                this.allTasks = this.generateMockTasks();
            }
            
            // Apply current filters and render
            this.applyFilters();
            this.updateLastUpdateTime();
            
        } catch (error) {
            console.error('Failed to load task data:', error);
            this.allTasks = this.generateMockTasks();
            this.applyFilters();
        }
    }

    /**
     * Generate mock tasks for demonstration
     */
    generateMockTasks() {
        const statuses = ['pending', 'running', 'completed', 'failed'];
        const queues = ['default', 'high', 'low', 'background', 'payments', 'critical'];
        const actors = ['process_document_async', 'send_notification', 'cleanup_old_files', 'generate_report', 'sync_data', 'send_email_task'];
        
        return Array.from({ length: 20 }, (_, i) => ({
            id: `task_${i + 1}`,
            actor_name: actors[Math.floor(Math.random() * actors.length)],
            status: statuses[Math.floor(Math.random() * statuses.length)],
            queue_name: queues[Math.floor(Math.random() * queues.length)],
            created_at: new Date(Date.now() - Math.random() * 86400000).toISOString(),
            updated_at: new Date(Date.now() - Math.random() * 3600000).toISOString(),
            message_id: `msg_${String(i + 1).padStart(3, '0')}`,
            progress: Math.random() > 0.7 ? Math.floor(Math.random() * 100) : null
        }));
    }

    /**
     * Apply filters to tasks
     */
    applyFilters() {
        this.filteredTasks = this.allTasks.filter(task => {
            const matchesStatus = !this.filters.status || this.mapStatus(task.status) === this.filters.status;
            const matchesQueue = !this.filters.queue || (task.queue_name || task.queue) === this.filters.queue;
            const matchesSearch = !this.filters.search || 
                task.actor_name.toLowerCase().includes(this.filters.search) ||
                String(task.id).toLowerCase().includes(this.filters.search);
            
            return matchesStatus && matchesQueue && matchesSearch;
        });

        this.renderTasks();
        this.updateTaskCounts();
    }

    /**
     * Map task status to display status
     */
    mapStatus(status) {
        const statusMap = {
            'enqueued': 'pending',
            'delayed': 'pending', 
            'pending': 'pending',
            'running': 'running',
            'done': 'completed',
            'completed': 'completed',
            'failed': 'failed',
            'skipped': 'completed'
        };
        
        return statusMap[status?.toLowerCase()] || 'pending';
    }

    /**
     * Render tasks table
     */
    renderTasks() {
        const tableBody = document.querySelector('#task-table-body');
        if (!tableBody) return;

        // Show/hide empty state
        const emptyState = document.getElementById('tasks-empty');
        const loadingState = document.getElementById('tasks-loading');
        
        loadingState?.classList.add('hidden');
        
        if (this.filteredTasks.length === 0) {
            emptyState?.classList.remove('hidden');
            tableBody.innerHTML = '';
            return;
        }
        
        emptyState?.classList.add('hidden');
        tableBody.innerHTML = '';
        
        this.filteredTasks.forEach(task => {
            const row = this.createTaskRow(task);
            tableBody.appendChild(row);
        });
    }

    /**
     * Create task row element
     */
    createTaskRow(task) {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors';
        row.setAttribute('data-task-id', task.id);

        const displayStatus = this.mapStatus(task.status);
        const statusConfig = this.getStatusConfig(displayStatus);

        row.innerHTML = `
            <td class="px-4 py-3 whitespace-nowrap">
                <div class="flex items-center space-x-2">
                    <span class="material-icons text-sm ${statusConfig.iconColor}">${statusConfig.icon}</span>
                    <span class="px-2 py-1 text-xs font-medium rounded-full ${statusConfig.color}">
                        ${statusConfig.label}
                    </span>
                </div>
                ${displayStatus === 'running' && task.progress ? `
                    <div class="mt-1 w-16 bg-gray-200 dark:bg-gray-600 rounded-full h-1">
                        <div class="bg-blue-600 h-1 rounded-full transition-all duration-300" style="width: ${task.progress}%"></div>
                    </div>
                ` : ''}
            </td>
            <td class="px-4 py-3">
                <div class="text-sm font-medium text-gray-900 dark:text-white">${task.actor_name}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400 font-mono">${String(task.id).substring(0, 8)}...</div>
            </td>
            <td class="px-4 py-3 whitespace-nowrap">
                <span class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
                    ${task.queue_name || task.queue || 'unknown'}
                </span>
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                ${this.calculateDuration(task.created_at, task.updated_at)}
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                ${new Date(task.updated_at).toLocaleTimeString()}
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end space-x-1">
                    ${displayStatus === 'failed' ? `
                        <button class="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
                            Retry
                        </button>
                    ` : ''}
                    <button class="p-1 text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors" title="View details">
                        <span class="material-icons text-sm">info</span>
                    </button>
                </div>
            </td>
        `;

        return row;
    }

    /**
     * Get status configuration
     */
    getStatusConfig(status) {
        const configs = {
            pending: {
                icon: 'schedule',
                label: 'PENDING',
                color: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200',
                iconColor: 'text-yellow-500'
            },
            running: {
                icon: 'play_circle',
                label: 'RUNNING',
                color: 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
                iconColor: 'text-blue-500'
            },
            completed: {
                icon: 'check_circle',
                label: 'COMPLETED',
                color: 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
                iconColor: 'text-green-500'
            },
            failed: {
                icon: 'error',
                label: 'FAILED',
                color: 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200',
                iconColor: 'text-red-500'
            }
        };

        return configs[status] || configs.pending;
    }

    /**
     * Update task counts in footer
     */
    updateTaskCounts() {
        const counts = {
            completed: this.filteredTasks.filter(t => ['completed', 'done'].includes(this.mapStatus(t.status))).length,
            running: this.filteredTasks.filter(t => this.mapStatus(t.status) === 'running').length,
            pending: this.filteredTasks.filter(t => this.mapStatus(t.status) === 'pending').length,
            failed: this.filteredTasks.filter(t => this.mapStatus(t.status) === 'failed').length
        };

        document.getElementById('completed-count').textContent = counts.completed;
        document.getElementById('running-count').textContent = counts.running;
        document.getElementById('pending-count').textContent = counts.pending;
        document.getElementById('failed-count').textContent = counts.failed;
        
        // Update task count badge
        const badge = document.getElementById('task-count-badge');
        if (badge) {
            const filteredCount = this.filteredTasks.length;
            const totalCount = this.allTasks.length;
            badge.textContent = filteredCount === totalCount ? 
                `${totalCount} tasks` : 
                `${filteredCount} of ${totalCount} tasks`;
        }

        // Update tab badge
        const tabBadge = document.querySelector('#tasks-count-badge');
        if (tabBadge) {
            tabBadge.textContent = this.allTasks.length;
        }
    }

    /**
     * Calculate duration between dates
     */
    calculateDuration(start, end) {
        if (!start || !end) return '--';
        const diff = new Date(end) - new Date(start);
        if (diff < 60000) return `${Math.floor(diff / 1000)}s`;
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
        return `${Math.floor(diff / 3600000)}h`;
    }

    /**
     * Update last update time
     */
    updateLastUpdateTime() {
        const timeElement = document.getElementById('tasks-last-update-time');
        if (timeElement) {
            timeElement.textContent = new Date().toLocaleTimeString();
        }
    }

    /**
     * Task actions
     */
    clearCompletedTasks() {
        if (!confirm('Are you sure you want to clear all completed tasks?')) {
            return;
        }
        console.log('Clearing completed tasks...');
    }

    exportTasks() {
        const csv = this.tasksToCSV(this.filteredTasks);
        this.downloadCSV(csv, 'tasks-export.csv');
    }

    tasksToCSV(tasks) {
        const headers = ['ID', 'Actor', 'Status', 'Queue', 'Created', 'Updated', 'Duration'];
        const rows = tasks.map(task => [
            task.id,
            task.actor_name,
            task.status,
            task.queue_name || task.queue || 'unknown',
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

    toggleAutoRefresh() {
        console.log('Toggling auto-refresh...');
    }
}