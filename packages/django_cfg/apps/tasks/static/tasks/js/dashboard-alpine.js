/**
 * Tasks Dashboard Alpine.js Logic
 *
 * This file extends Alpine.js data and methods for the Tasks Dashboard.
 * It integrates with the tasksAPI to provide reactive state management.
 *
 * TODO: Refactor into modular structure:
 * - alpine/state.js - Initial state
 * - alpine/loaders/ - Data loading methods (loadOverview, loadQueues, loadWorkers, loadTasks)
 * - alpine/actions/ - User actions (simulate, clear, purge, start/stop workers, etc)
 * - alpine/utils/ - Utility functions (formatters, helpers)
 * - alpine/index.js - Main entry combining all modules
 *
 * Current size: 716 lines (needs decomposition for maintainability)
 */

// Wait for Alpine.js to be available
document.addEventListener('alpine:init', () => {
    console.log('🚀 Initializing Alpine.js Dashboard extensions...');

    // Extend Alpine.js global data/methods
    Alpine.data('tasksDashboard', () => ({
        // Alpine.js state for Tasks Dashboard
        activeTab: 'overview',
        loading: false,
        autoRefresh: true,
        autoRefreshInterval: null,
        lastUpdateTime: '--:--:--',

        // Data collections
        tasks: [],
        queues: [],
        workers: [],
        stats: {},

        // Filters
        filters: {
            status: '',
            queue: '',
            search: ''
        },

        // Counts for badges
        counts: {
            queues: 0,
            workers: 0,
            tasks: 0
        },

        // Action message state
        actionMessage: '',
        actionType: 'info', // 'info', 'success', 'error'

        // Modal state
        showTaskModal: false,
        selectedTask: null,

        // Pagination state
        pagination: {
            page: 1,
            page_size: 20,
            total_pages: 1,
            total_count: 0,
            has_next: false,
            has_previous: false
        },

        // Lifecycle init
        init() {
            console.log('🎯 Dashboard component initialized');

            // Initialize dashboard data
            this.loadDashboardData();

            // Start auto-refresh if enabled
            if (this.autoRefresh) {
                this.startAutoRefresh();
            }

            // Watch for tab changes
            this.$watch('activeTab', (value) => {
                console.log('Tab changed to:', value);
                this.onTabChange(value);
            });
        },

        // Computed properties
        get filteredTasks() {
            let filtered = this.tasks;

            // Apply status filter
            if (this.filters.status) {
                filtered = filtered.filter(task => task.status === this.filters.status);
            }

            // Apply queue filter
            if (this.filters.queue) {
                filtered = filtered.filter(task =>
                    (task.queue || task.queue_name) === this.filters.queue
                );
            }

            // Apply search filter
            if (this.filters.search) {
                const search = this.filters.search.toLowerCase();
                filtered = filtered.filter(task =>
                    task.name?.toLowerCase().includes(search) ||
                    task.actor_name?.toLowerCase().includes(search) ||
                    task.task_id?.toLowerCase().includes(search) ||
                    task.message_id?.toLowerCase().includes(search) ||
                    task.queue?.toLowerCase().includes(search) ||
                    task.queue_name?.toLowerCase().includes(search)
                );
            }

            return filtered;
        },

        // Methods
        async loadDashboardData() {
            console.log('📊 Loading dashboard data...');
            this.loading = true;

            try {
                // Load all data in parallel
                await Promise.all([
                    this.loadOverview(),
                    this.loadQueues(),
                    this.loadWorkers(),
                    this.loadTasks()
                ]);

                this.updateLastUpdateTime();
                console.log('✅ Dashboard data loaded successfully');
            } catch (error) {
                console.error('❌ Failed to load dashboard data:', error);
                if (window.showNotification) {
                    window.showNotification('Failed to load dashboard data', 'error');
                }
            } finally {
                this.loading = false;
            }
        },

        async loadOverview() {
            if (!window.tasksAPI) return;

            try {
                const response = await window.tasksAPI.tasksApiTasksStatsRetrieve();
                const data = response?.data || response || {};

                // Flatten statistics into stats for easier access in template
                if (data.statistics) {
                    this.stats = {
                        ...data,
                        ...data.statistics,
                        // Map API fields to template fields
                        total_tasks: data.statistics.total || 0,
                        completed_tasks: data.statistics.completed || 0,
                        running_tasks: data.statistics.running || 0,
                        failed_tasks: data.statistics.failed || 0,
                        pending_tasks: data.statistics.pending || 0,
                        success_rate: (data.statistics.success_rate || 0) / 100 // Convert from % to decimal
                    };
                } else {
                    this.stats = data;
                }

                // Update counts
                this.counts.queues = this.stats.active_queues || 0;
                // Note: workers count is updated in loadWorkers()
                this.counts.tasks = this.stats.total_tasks || 0;

                console.log('📈 Overview stats loaded:', this.stats);
            } catch (error) {
                console.error('Failed to load overview:', error);
            }
        },

        async loadQueues() {
            if (!window.tasksAPI) return;

            try {
                const response = await window.tasksAPI.tasksApiQueuesStatusRetrieve();
                const queuesData = response?.data?.queues || response?.queues;

                // Convert queues object to array if needed
                if (queuesData && typeof queuesData === 'object' && !Array.isArray(queuesData)) {
                    this.queues = Object.entries(queuesData).map(([name, data]) => ({
                        name,
                        ...data
                    }));
                } else {
                    this.queues = queuesData || [];
                }

                this.counts.queues = this.queues.length;

                console.log('📋 Queues loaded:', this.queues.length);
            } catch (error) {
                console.error('Failed to load queues:', error);
            }
        },

        async loadWorkers() {
            if (!window.tasksAPI) return;

            try {
                const response = await window.tasksAPI.tasksApiWorkersListRetrieve();
                const data = response?.data || response || {};

                this.workers = data.workers || [];
                this.counts.workers = data.active_count || this.workers.length;

                // Update stats.workers for overview display
                this.stats.workers = this.counts.workers;

                console.log('👷 Workers loaded:', this.workers.length, 'Active:', this.counts.workers);
            } catch (error) {
                console.error('Failed to load workers:', error);
            }
        },

        async loadTasks(page = 1) {
            if (!window.tasksAPI) return;

            try {
                // TODO: Pass page parameter to API when backend supports it
                const response = await window.tasksAPI.tasksApiTasksListRetrieve();
                const data = response?.data || response || {};

                this.tasks = data.tasks || [];

                // Update pagination info
                if (data.pagination) {
                    this.pagination = {
                        page: data.pagination.page || 1,
                        page_size: data.pagination.page_size || 20,
                        total_pages: data.pagination.total_pages || 1,
                        total_count: data.pagination.total_count || this.tasks.length,
                        has_next: data.pagination.has_next || false,
                        has_previous: data.pagination.has_previous || false
                    };
                }

                this.counts.tasks = this.pagination.total_count;

                console.log('📝 Tasks loaded:', this.tasks.length, 'Total:', this.pagination.total_count);
            } catch (error) {
                console.error('Failed to load tasks:', error);
            }
        },

        // Pagination methods
        nextPage() {
            if (this.pagination.has_next) {
                this.loadTasks(this.pagination.page + 1);
            }
        },

        previousPage() {
            if (this.pagination.has_previous) {
                this.loadTasks(this.pagination.page - 1);
            }
        },

        goToPage(page) {
            if (page >= 1 && page <= this.pagination.total_pages) {
                this.loadTasks(page);
            }
        },

        applyFilters() {
            console.log('🔍 Applying filters:', this.filters);
            // The filteredTasks computed property will automatically update
        },

        toggleAutoRefresh() {
            this.autoRefresh = !this.autoRefresh;

            if (this.autoRefresh) {
                this.startAutoRefresh();
                console.log('✅ Auto-refresh enabled');
            } else {
                this.stopAutoRefresh();
                console.log('⏸️ Auto-refresh disabled');
            }
        },

        startAutoRefresh() {
            // Clear existing interval
            this.stopAutoRefresh();

            // Set new interval (refresh every 5 seconds)
            this.autoRefreshInterval = setInterval(() => {
                console.log('🔄 Auto-refresh triggered');
                this.loadDashboardData();
            }, 5000);
        },

        stopAutoRefresh() {
            if (this.autoRefreshInterval) {
                clearInterval(this.autoRefreshInterval);
                this.autoRefreshInterval = null;
            }
        },

        updateLastUpdateTime() {
            const now = new Date();
            this.lastUpdateTime = now.toLocaleTimeString('en-US', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        },

        onTabChange(tab) {
            console.log(`🔄 Switched to ${tab} tab`);

            // Load data for specific tab if not loaded
            switch (tab) {
                case 'overview':
                    if (Object.keys(this.stats).length === 0) {
                        this.loadOverview();
                    }
                    break;
                case 'queues':
                    if (this.queues.length === 0) {
                        this.loadQueues();
                    }
                    break;
                case 'workers':
                    if (this.workers.length === 0) {
                        this.loadWorkers();
                    }
                    break;
                case 'tasks':
                    if (this.tasks.length === 0) {
                        this.loadTasks();
                    }
                    break;
            }
        },

        // Task management methods
        async clearAllTasks() {
            if (!confirm('Are you sure you want to clear all tasks?')) {
                return;
            }

            try {
                this.loading = true;
                this.showActionMessage('Clearing all tasks...', 'info');
                await window.tasksAPI.tasksApiClearCreate({});
                await this.loadTasks();

                this.showActionMessage('All tasks cleared successfully', 'success');

                if (window.showNotification) {
                    window.showNotification('All tasks cleared successfully', 'success');
                }

                console.log('✅ All tasks cleared');
            } catch (error) {
                console.error('❌ Failed to clear tasks:', error);
                this.showActionMessage('Failed to clear tasks: ' + error.message, 'error');

                if (window.showNotification) {
                    window.showNotification('Failed to clear tasks: ' + error.message, 'error');
                }
            } finally {
                this.loading = false;
            }
        },

        async clearAllQueues() {
            if (!confirm('Are you sure you want to clear all queues?')) {
                return;
            }

            try {
                this.loading = true;
                this.showActionMessage('Clearing all queues...', 'info');
                // Assuming there's an API endpoint for this
                await window.tasksAPI.tasksApiClearQueuesCreate({});
                await this.loadQueues();

                this.showActionMessage('All queues cleared successfully', 'success');

                if (window.showNotification) {
                    window.showNotification('All queues cleared successfully', 'success');
                }

                console.log('✅ All queues cleared');
            } catch (error) {
                console.error('❌ Failed to clear queues:', error);
                this.showActionMessage('Failed to clear queues: ' + error.message, 'error');

                if (window.showNotification) {
                    window.showNotification('Failed to clear queues: ' + error.message, 'error');
                }
            } finally {
                this.loading = false;
            }
        },

        async purgeFailedTasks() {
            if (!confirm('Are you sure you want to purge all failed tasks?')) {
                return;
            }

            try {
                this.loading = true;
                this.showActionMessage('Purging failed tasks...', 'info');
                // Assuming there's an API endpoint for this
                await window.tasksAPI.tasksApiPurgeFailedCreate({});
                await this.loadTasks();

                this.showActionMessage('Failed tasks purged successfully', 'success');

                if (window.showNotification) {
                    window.showNotification('Failed tasks purged successfully', 'success');
                }

                console.log('✅ Failed tasks purged');
            } catch (error) {
                console.error('❌ Failed to purge failed tasks:', error);
                this.showActionMessage('Failed to purge failed tasks: ' + error.message, 'error');

                if (window.showNotification) {
                    window.showNotification('Failed to purge failed tasks: ' + error.message, 'error');
                }
            } finally {
                this.loading = false;
            }
        },

        async simulateTasks(count = 5) {
            try {
                this.loading = true;
                this.showActionMessage(`Simulating ${count} tasks...`, 'info');
                await window.tasksAPI.tasksApiSimulateCreate({
                    count: count,
                    queue: 'default',
                    task_type: 'test'
                });
                await this.loadTasks();

                this.showActionMessage(`Simulated ${count} tasks successfully`, 'success');

                if (window.showNotification) {
                    window.showNotification(`Simulated ${count} tasks successfully`, 'success');
                }

                console.log(`✅ Simulated ${count} tasks`);
            } catch (error) {
                console.error('❌ Failed to simulate tasks:', error);
                this.showActionMessage('Failed to simulate tasks: ' + error.message, 'error');

                if (window.showNotification) {
                    window.showNotification('Failed to simulate tasks: ' + error.message, 'error');
                }
            } finally {
                this.loading = false;
            }
        },

        showActionMessage(message, type = 'info') {
            this.actionMessage = message;
            this.actionType = type;

            // Auto-hide after 5 seconds
            setTimeout(() => {
                this.actionMessage = '';
            }, 5000);
        },

        async startWorkers() {
            try {
                this.loading = true;
                this.showActionMessage('Starting workers...', 'info');
                await window.tasksAPI.tasksApiWorkersManageCreate({ action: 'start' });
                await this.loadWorkers();

                this.showActionMessage('Workers started successfully', 'success');

                if (window.showNotification) {
                    window.showNotification('Workers started successfully', 'success');
                }

                console.log('✅ Workers started');
            } catch (error) {
                console.error('❌ Failed to start workers:', error);
                this.showActionMessage('Failed to start workers: ' + error.message, 'error');

                if (window.showNotification) {
                    window.showNotification('Failed to start workers: ' + error.message, 'error');
                }
            } finally {
                this.loading = false;
            }
        },

        async stopWorkers() {
            if (!confirm('Are you sure you want to stop all workers?')) {
                return;
            }

            try {
                this.loading = true;
                this.showActionMessage('Stopping workers...', 'info');
                await window.tasksAPI.tasksApiWorkersManageCreate({ action: 'stop' });
                await this.loadWorkers();

                this.showActionMessage('Workers stopped successfully', 'success');

                if (window.showNotification) {
                    window.showNotification('Workers stopped successfully', 'success');
                }

                console.log('✅ Workers stopped');
            } catch (error) {
                console.error('❌ Failed to stop workers:', error);
                this.showActionMessage('Failed to stop workers: ' + error.message, 'error');

                if (window.showNotification) {
                    window.showNotification('Failed to stop workers: ' + error.message, 'error');
                }
            } finally {
                this.loading = false;
            }
        },

        // Task status helpers
        getStatusColor(status) {
            const colors = {
                'pending': 'yellow',
                'running': 'blue',
                'completed': 'green',
                'failed': 'red'
            };
            return colors[status] || 'gray';
        },

        formatDuration(ms) {
            if (!ms) return '-';

            if (ms < 1000) {
                return `${ms}ms`;
            } else if (ms < 60000) {
                return `${(ms / 1000).toFixed(1)}s`;
            } else {
                return `${(ms / 60000).toFixed(1)}m`;
            }
        },

        formatDate(dateString) {
            if (!dateString) return '-';

            try {
                const date = new Date(dateString);
                return date.toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
            } catch (error) {
                return dateString;
            }
        },

        // Task action methods
        async viewTaskDetails(task) {
            console.log('View task details:', task);
            this.selectedTask = task;
            this.showTaskModal = true;
        },

        closeTaskModal() {
            this.showTaskModal = false;
            // Clear selected task after transition
            setTimeout(() => {
                this.selectedTask = null;
            }, 300);
        },

        async retryTask(task) {
            // TODO: Implement retry task endpoint in backend API
            this.showActionMessage('Retry task feature is not yet implemented', 'error');

            if (window.showNotification) {
                window.showNotification('Retry task feature is not yet implemented', 'error');
            }

            console.warn('⚠️ Retry task endpoint not implemented in API');
        },

        async deleteTask(task) {
            // TODO: Implement delete task endpoint in backend API
            this.showActionMessage('Delete task feature is not yet implemented', 'error');

            if (window.showNotification) {
                window.showNotification('Delete task feature is not yet implemented', 'error');
            }

            console.warn('⚠️ Delete task endpoint not implemented in API');
        },

        // Footer action methods
        async clearCompletedTasks() {
            // TODO: Implement clear completed tasks endpoint in backend API
            this.showActionMessage('Clear completed tasks feature is not yet implemented', 'error');

            if (window.showNotification) {
                window.showNotification('Clear completed tasks feature is not yet implemented', 'error');
            }

            console.warn('⚠️ Clear completed tasks endpoint not implemented in API');
        },

        async exportTasksCSV() {
            try {
                this.showActionMessage('Exporting tasks to CSV...', 'info');

                // Simple CSV export implementation
                const headers = ['ID', 'Name', 'Status', 'Queue', 'Duration', 'Created', 'Updated'];
                const rows = this.tasks.map(task => [
                    task.task_id || task.id,
                    task.name,
                    task.status,
                    task.queue || 'default',
                    task.duration || '',
                    task.created_at || '',
                    task.updated_at || ''
                ]);

                const csvContent = [
                    headers.join(','),
                    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
                ].join('\n');

                // Create blob and download
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);

                link.setAttribute('href', url);
                link.setAttribute('download', `tasks_export_${new Date().toISOString().split('T')[0]}.csv`);
                link.style.visibility = 'hidden';

                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                this.showActionMessage('Tasks exported successfully', 'success');

                if (window.showNotification) {
                    window.showNotification('Tasks exported to CSV', 'success');
                }

                console.log('✅ Tasks exported to CSV');
            } catch (error) {
                console.error('❌ Failed to export tasks:', error);
                this.showActionMessage('Failed to export tasks: ' + error.message, 'error');

                if (window.showNotification) {
                    window.showNotification('Failed to export tasks: ' + error.message, 'error');
                }
            }
        }
    }));
});

// Add global helper functions for Alpine.js templates
window.dashboardHelpers = {
    formatDuration: (ms) => {
        if (!ms) return '-';

        if (ms < 1000) {
            return `${ms}ms`;
        } else if (ms < 60000) {
            return `${(ms / 1000).toFixed(1)}s`;
        } else {
            return `${(ms / 60000).toFixed(1)}m`;
        }
    },

    formatDate: (dateString) => {
        if (!dateString) return '-';

        try {
            const date = new Date(dateString);
            return date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch (error) {
            return dateString;
        }
    },

    getStatusBadgeClass: (status) => {
        const classes = {
            'pending': 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200',
            'running': 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
            'completed': 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
            'failed': 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
        };
        return classes[status] || 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
};

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    console.log('🧹 Cleaning up dashboard...');
    // Alpine.js will handle cleanup automatically
});

console.log('✅ Dashboard Alpine.js extensions loaded');
