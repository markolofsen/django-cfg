/**
 * Management Actions - Clear, Purge, Simulate
 */

export async function clearAllTasks() {
    if (!confirm('Are you sure you want to clear all tasks?')) {
        return;
    }

    try {
        this.loading = true;
        this.showActionMessage('Clearing all tasks...', 'info');
        await window.tasksAPI.tasksApiClearCreate({});
        await this.loadTasks();

        this.showActionMessage('All tasks cleared successfully', 'success');

        if (window.showNotification) {
            window.showNotification('All tasks cleared successfully', 'success');
        }

        console.log('✅ All tasks cleared');
    } catch (error) {
        console.error('❌ Failed to clear tasks:', error);
        this.showActionMessage('Failed to clear tasks: ' + error.message, 'error');

        if (window.showNotification) {
            window.showNotification('Failed to clear tasks: ' + error.message, 'error');
        }
    } finally {
        this.loading = false;
    }
}

export async function clearAllQueues() {
    if (!confirm('Are you sure you want to clear all queues?')) {
        return;
    }

    try {
        this.loading = true;
        this.showActionMessage('Clearing all queues...', 'info');
        await window.tasksAPI.tasksApiClearQueuesCreate({});
        await this.loadQueues();

        this.showActionMessage('All queues cleared successfully', 'success');

        if (window.showNotification) {
            window.showNotification('All queues cleared successfully', 'success');
        }

        console.log('✅ All queues cleared');
    } catch (error) {
        console.error('❌ Failed to clear queues:', error);
        this.showActionMessage('Failed to clear queues: ' + error.message, 'error');

        if (window.showNotification) {
            window.showNotification('Failed to clear queues: ' + error.message, 'error');
        }
    } finally {
        this.loading = false;
    }
}

export async function purgeFailedTasks() {
    if (!confirm('Are you sure you want to purge all failed tasks?')) {
        return;
    }

    try {
        this.loading = true;
        this.showActionMessage('Purging failed tasks...', 'info');
        await window.tasksAPI.tasksApiPurgeFailedCreate({});
        await this.loadTasks();

        this.showActionMessage('Failed tasks purged successfully', 'success');

        if (window.showNotification) {
            window.showNotification('Failed tasks purged successfully', 'success');
        }

        console.log('✅ Failed tasks purged');
    } catch (error) {
        console.error('❌ Failed to purge failed tasks:', error);
        this.showActionMessage('Failed to purge failed tasks: ' + error.message, 'error');

        if (window.showNotification) {
            window.showNotification('Failed to purge failed tasks: ' + error.message, 'error');
        }
    } finally {
        this.loading = false;
    }
}

export async function simulateTasks(count = 5) {
    try {
        this.loading = true;
        this.showActionMessage(`Simulating ${count} tasks...`, 'info');
        await window.tasksAPI.tasksApiSimulateCreate({
            count: count,
            queue: 'default',
            task_type: 'test'
        });
        await this.loadTasks();

        this.showActionMessage(`Simulated ${count} tasks successfully`, 'success');

        if (window.showNotification) {
            window.showNotification(`Simulated ${count} tasks successfully`, 'success');
        }

        console.log(`✅ Simulated ${count} tasks`);
    } catch (error) {
        console.error('❌ Failed to simulate tasks:', error);
        this.showActionMessage('Failed to simulate tasks: ' + error.message, 'error');

        if (window.showNotification) {
            window.showNotification('Failed to simulate tasks: ' + error.message, 'error');
        }
    } finally {
        this.loading = false;
    }
}
