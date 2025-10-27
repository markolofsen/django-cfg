/**
 * Data Loaders - Load data from API endpoints
 */

export { loadOverview } from './overview.js';
export { loadQueues } from './queues.js';
export { loadWorkers } from './workers.js';
export { loadTasks } from './tasks.js';

/**
 * Load all dashboard data in parallel
 */
export async function loadDashboardData() {
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
}
