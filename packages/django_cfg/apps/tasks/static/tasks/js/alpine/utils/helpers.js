/**
 * Helper Utilities
 */

export function updateLastUpdateTime() {
    const now = new Date();
    this.lastUpdateTime = now.toLocaleTimeString('en-US', { hour12: false });
}

export function showActionMessage(message, type = 'info') {
    this.actionMessage = message;
    this.actionType = type;

    // Auto-hide after 5 seconds
    setTimeout(() => {
        this.actionMessage = '';
    }, 5000);
}

export function applyFilters() {
    console.log('🔍 Applying filters:', this.filters);
    // The filteredTasks computed property will automatically update
}

export function toggleAutoRefresh() {
    this.autoRefresh = !this.autoRefresh;

    if (this.autoRefresh) {
        this.startAutoRefresh();
    } else {
        this.stopAutoRefresh();
    }
}

export function startAutoRefresh() {
    if (this.autoRefreshInterval) {
        clearInterval(this.autoRefreshInterval);
    }

    // Refresh every 30 seconds
    this.autoRefreshInterval = setInterval(() => {
        if (!this.loading) {
            this.loadDashboardData();
        }
    }, 30000);

    console.log('✅ Auto-refresh started (30s interval)');
}

export function stopAutoRefresh() {
    if (this.autoRefreshInterval) {
        clearInterval(this.autoRefreshInterval);
        this.autoRefreshInterval = null;
    }
    console.log('⏸️ Auto-refresh stopped');
}

export function onTabChange(tabName) {
    console.log(`Switched to ${tabName} tab`);
    // Refresh data for the active tab if needed
    if (tabName === 'tasks') {
        this.loadTasks();
    } else if (tabName === 'workers') {
        this.loadWorkers();
    } else if (tabName === 'queues') {
        this.loadQueues();
    }
}
