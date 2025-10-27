/**
 * Computed Properties (as regular functions, not getters)
 * Alpine.js will reactively call these when dependencies change
 */

export function filteredTasks() {
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
}
