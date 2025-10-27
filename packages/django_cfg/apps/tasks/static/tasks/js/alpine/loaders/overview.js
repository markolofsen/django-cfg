/**
 * Load Overview Statistics
 */
export async function loadOverview() {
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
}
