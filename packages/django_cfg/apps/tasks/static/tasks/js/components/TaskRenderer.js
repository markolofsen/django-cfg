/**
 * TaskRenderer - Renders tasks using HTML templates (no HTML in JS!)
 */
export class TaskRenderer {
    constructor() {
        this.taskRowTemplate = document.getElementById('task-row-template');
        this.statusConfig = {
            pending: {
                icon: 'schedule',
                label: 'PENDING',
                color: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200',
                iconColor: 'text-yellow-500'
            },
            running: {
                icon: 'play_circle',
                label: 'RUNNING',
                color: 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
                iconColor: 'text-blue-500'
            },
            completed: {
                icon: 'check_circle',
                label: 'COMPLETED',
                color: 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
                iconColor: 'text-green-500'
            },
            failed: {
                icon: 'error',
                label: 'FAILED',
                color: 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200',
                iconColor: 'text-red-500'
            }
        };
    }

    /**
     * Render tasks into the table
     * @param {Array} tasks - Array of task objects
     * @param {HTMLElement} container - Container element
     */
    renderTasks(tasks, container) {
        const tableBody = container.querySelector('#task-table-body');
        if (!tableBody) return;

        // Clear existing rows
        tableBody.innerHTML = '';

        // Render each task
        tasks.forEach(task => {
            const row = this.createTaskRow(task);
            if (row) {
                tableBody.appendChild(row);
            }
        });
    }

    /**
     * Create a task row element using template
     * @param {Object} task - Task object
     * @returns {HTMLElement} - Task row element
     */
    createTaskRow(task) {
        if (!this.taskRowTemplate) {
            console.error('Task row template not found');
            return null;
        }

        // Clone template
        const row = this.taskRowTemplate.content.cloneNode(true).querySelector('.task-row');
        
        // Set task ID
        row.setAttribute('data-task-id', task.id);

        // Map status
        const displayStatus = this.mapStatus(task.status);
        const statusConfig = this.statusConfig[displayStatus];

        // Populate status
        const statusIcon = row.querySelector('.task-status-icon');
        const statusBadge = row.querySelector('.task-status-badge');
        
        if (statusIcon && statusBadge && statusConfig) {
            statusIcon.textContent = statusConfig.icon;
            statusIcon.className = `material-icons text-sm ${statusConfig.iconColor}`;
            
            statusBadge.textContent = statusConfig.label;
            statusBadge.className = `px-2 py-1 text-xs font-medium rounded-full ${statusConfig.color}`;
        }

        // Show progress bar for running tasks
        if (displayStatus === 'running' && task.progress) {
            const progressContainer = row.querySelector('.task-progress');
            const progressBar = progressContainer?.querySelector('div');
            if (progressContainer && progressBar) {
                progressContainer.classList.remove('hidden');
                progressBar.style.width = `${task.progress}%`;
            }
        }

        // Populate task info
        const taskName = row.querySelector('.task-name');
        const taskId = row.querySelector('.task-id');
        if (taskName) taskName.textContent = task.actor_name || 'Unknown Task';
        if (taskId) taskId.textContent = `${String(task.id).substring(0, 8)}...`;

        // Populate queue
        const taskQueue = row.querySelector('.task-queue');
        if (taskQueue) taskQueue.textContent = task.queue_name || task.queue || 'unknown';

        // Populate duration and time
        const taskDuration = row.querySelector('.task-duration');
        const taskUpdated = row.querySelector('.task-updated');
        if (taskDuration) taskDuration.textContent = this.calculateDuration(task.created_at, task.updated_at);
        if (taskUpdated) taskUpdated.textContent = new Date(task.updated_at).toLocaleTimeString();

        // Populate actions
        this.populateActions(row, task, displayStatus);

        return row;
    }

    /**
     * Map task status to display status
     * @param {string} status - Original status
     * @returns {string} - Mapped status
     */
    mapStatus(status) {
        const statusMap = {
            'enqueued': 'pending',
            'delayed': 'pending', 
            'pending': 'pending',
            'running': 'running',
            'done': 'completed',
            'completed': 'completed',
            'failed': 'failed',
            'skipped': 'completed'
        };
        
        return statusMap[status?.toLowerCase()] || 'pending';
    }

    /**
     * Populate task actions (no HTML strings!)
     * @param {HTMLElement} row - Task row element
     * @param {Object} task - Task object
     * @param {string} displayStatus - Display status
     */
    populateActions(row, task, displayStatus) {
        const actionsContainer = row.querySelector('.task-actions');
        if (!actionsContainer) return;
        
        actionsContainer.innerHTML = '';

        // Add retry button for failed tasks
        if (displayStatus === 'failed') {
            const retryBtn = document.createElement('button');
            retryBtn.className = 'px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors';
            retryBtn.textContent = 'Retry';
            retryBtn.addEventListener('click', () => this.retryTask(task.id));
            actionsContainer.appendChild(retryBtn);
        }

        // Add details button if task has additional info
        if (task.args || task.kwargs || task.result || task.traceback) {
            const detailsBtn = document.createElement('button');
            detailsBtn.className = 'p-1 text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors';
            detailsBtn.title = 'Show details';
            
            const icon = document.createElement('span');
            icon.className = 'material-icons text-sm';
            icon.textContent = 'info';
            detailsBtn.appendChild(icon);
            
            detailsBtn.addEventListener('click', () => this.showTaskDetails(task));
            actionsContainer.appendChild(detailsBtn);
        }
    }

    /**
     * Calculate duration between two dates
     * @param {string} startTime - Start time ISO string
     * @param {string} endTime - End time ISO string
     * @returns {string} - Formatted duration
     */
    calculateDuration(startTime, endTime) {
        if (!startTime || !endTime) return '--';
        
        const start = new Date(startTime);
        const end = new Date(endTime);
        const diff = end - start;
        
        if (diff < 1000) return `${diff}ms`;
        if (diff < 60000) return `${Math.floor(diff / 1000)}s`;
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ${Math.floor((diff % 60000) / 1000)}s`;
        return `${Math.floor(diff / 3600000)}h ${Math.floor((diff % 3600000) / 60000)}m`;
    }

    /**
     * Retry a failed task
     * @param {string} taskId - Task ID
     */
    retryTask(taskId) {
        console.log('Retrying task:', taskId);
        // TODO: Implement retry functionality
        alert(`Retry functionality for task ${taskId} will be implemented`);
    }

    /**
     * Show task details
     * @param {Object} task - Task object
     */
    showTaskDetails(task) {
        console.log('Showing task details:', task);
        // TODO: Implement task details modal
        alert(`Task Details:\nID: ${task.id}\nActor: ${task.actor_name}\nStatus: ${task.status}`);
    }
}
