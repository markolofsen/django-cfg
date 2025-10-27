/**
 * Load Queues Status
 */
export async function loadQueues() {
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
}
