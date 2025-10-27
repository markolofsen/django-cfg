/**
 * Tasks Dashboard Alpine.js - Modular Version
 *
 * Entry point for modular Alpine.js dashboard component
 */

import initialState from './state.js';
import { filteredTasks } from './computed.js';

// Loaders
import {
    loadDashboardData,
    loadOverview,
    loadQueues,
    loadWorkers,
    loadTasks
} from './loaders/index.js';

// Actions
import {
    clearAllTasks,
    clearAllQueues,
    purgeFailedTasks,
    simulateTasks
} from './actions/management.js';

import {
    startWorkers,
    stopWorkers
} from './actions/workers.js';

import {
    viewTaskDetails,
    closeTaskModal,
    retryTask,
    deleteTask,
    clearCompletedTasks,
    exportTasksCSV
} from './actions/tasks.js';

import {
    nextPage,
    previousPage,
    goToPage
} from './actions/pagination.js';

// Utils
import {
    formatDuration,
    formatDate,
    getStatusColor
} from './utils/formatters.js';

import {
    updateLastUpdateTime,
    showActionMessage,
    applyFilters,
    toggleAutoRefresh,
    startAutoRefresh,
    stopAutoRefresh,
    onTabChange
} from './utils/helpers.js';

// Register component factory globally BEFORE Alpine loads
window.tasksDashboardComponent = () => ({
        // State
        ...initialState,

        // Computed properties (as method)
        filteredTasks,

        // Lifecycle
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

        // Data loading methods
        loadDashboardData,
        loadOverview,
        loadQueues,
        loadWorkers,
        loadTasks,

        // Management actions
        clearAllTasks,
        clearAllQueues,
        purgeFailedTasks,
        simulateTasks,

        // Worker actions
        startWorkers,
        stopWorkers,

        // Task actions
        viewTaskDetails,
        closeTaskModal,
        retryTask,
        deleteTask,
        clearCompletedTasks,
        exportTasksCSV,

        // Pagination
        nextPage,
        previousPage,
        goToPage,

        // Formatters
        formatDuration,
        formatDate,
        getStatusColor,

        // Helpers
        updateLastUpdateTime,
        showActionMessage,
        applyFilters,
        toggleAutoRefresh,
        startAutoRefresh,
        stopAutoRefresh,
        onTabChange
    });

// Register with Alpine when it initializes
document.addEventListener('alpine:init', () => {
    console.log('🚀 Registering tasksDashboard component with Alpine...');
    window.Alpine.data('tasksDashboard', window.tasksDashboardComponent);
    console.log('✅ Dashboard Alpine.js extensions loaded (modular)');
});

// Export for potential external use
export default {
    initialState,
    filteredTasks,
    // Add other exports if needed
};
