/**
 * Task Management Actions
 */

export async function viewTaskDetails(task) {
    console.log('View task details:', task);
    this.selectedTask = task;
    this.showTaskModal = true;
}

export function closeTaskModal() {
    this.showTaskModal = false;
    // Clear selected task after transition
    setTimeout(() => {
        this.selectedTask = null;
    }, 300);
}

export async function retryTask(task) {
    // TODO: Implement retry task endpoint in backend API
    this.showActionMessage('Retry task feature is not yet implemented', 'error');

    if (window.showNotification) {
        window.showNotification('Retry task feature is not yet implemented', 'error');
    }

    console.warn('⚠️ Retry task endpoint not implemented in API');
}

export async function deleteTask(task) {
    // TODO: Implement delete task endpoint in backend API
    this.showActionMessage('Delete task feature is not yet implemented', 'error');

    if (window.showNotification) {
        window.showNotification('Delete task feature is not yet implemented', 'error');
    }

    console.warn('⚠️ Delete task endpoint not implemented in API');
}

export async function clearCompletedTasks() {
    // TODO: Implement clear completed tasks endpoint in backend API
    this.showActionMessage('Clear completed tasks feature is not yet implemented', 'error');

    if (window.showNotification) {
        window.showNotification('Clear completed tasks feature is not yet implemented', 'error');
    }

    console.warn('⚠️ Clear completed tasks endpoint not implemented in API');
}

export async function exportTasksCSV() {
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
