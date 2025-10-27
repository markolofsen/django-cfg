/**
 * Worker Management Actions
 */

export async function startWorkers() {
    try {
        this.loading = true;
        this.showActionMessage('Starting workers...', 'info');
        await window.tasksAPI.tasksApiWorkersManageCreate({ action: 'start' });
        await this.loadWorkers();

        this.showActionMessage('Workers started successfully', 'success');

        if (window.showNotification) {
            window.showNotification('Workers started successfully', 'success');
        }

        console.log('✅ Workers started');
    } catch (error) {
        console.error('❌ Failed to start workers:', error);
        this.showActionMessage('Failed to start workers: ' + error.message, 'error');

        if (window.showNotification) {
            window.showNotification('Failed to start workers: ' + error.message, 'error');
        }
    } finally {
        this.loading = false;
    }
}

export async function stopWorkers() {
    if (!confirm('Are you sure you want to stop all workers?')) {
        return;
    }

    try {
        this.loading = true;
        this.showActionMessage('Stopping workers...', 'info');
        await window.tasksAPI.tasksApiWorkersManageCreate({ action: 'stop' });
        await this.loadWorkers();

        this.showActionMessage('Workers stopped successfully', 'success');

        if (window.showNotification) {
            window.showNotification('Workers stopped successfully', 'success');
        }

        console.log('✅ Workers stopped');
    } catch (error) {
        console.error('❌ Failed to stop workers:', error);
        this.showActionMessage('Failed to stop workers: ' + error.message, 'error');

        if (window.showNotification) {
            window.showNotification('Failed to stop workers: ' + error.message, 'error');
        }
    } finally {
        this.loading = false;
    }
}
