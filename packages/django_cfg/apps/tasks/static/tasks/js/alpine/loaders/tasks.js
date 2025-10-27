/**
 * Load Tasks List with Pagination
 */
export async function loadTasks(page = 1) {
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
}
