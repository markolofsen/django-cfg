/**
 * Pagination Actions
 */

export function nextPage() {
    if (this.pagination.has_next) {
        this.loadTasks(this.pagination.page + 1);
    }
}

export function previousPage() {
    if (this.pagination.has_previous) {
        this.loadTasks(this.pagination.page - 1);
    }
}

export function goToPage(page) {
    if (page >= 1 && page <= this.pagination.total_pages) {
        this.loadTasks(page);
    }
}
