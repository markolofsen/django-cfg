/**
 * Load Workers List
 */
export async function loadWorkers() {
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
}
