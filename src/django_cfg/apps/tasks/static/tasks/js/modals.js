/**
 * Modal System for Dashboard
 * Handles modal dialogs and interactive components
 */

class ModalSystem {
    constructor() {
        this.activeModal = null;
        this.init();
    }

    /**
     * Initialize modal system
     */
    init() {
        this.createModalContainer();
        this.setupEventListeners();
    }

    /**
     * Create modal container
     */
    createModalContainer() {
        if (document.getElementById('modal-container')) return;

        const container = document.createElement('div');
        container.id = 'modal-container';
        container.className = 'fixed inset-0 z-50 hidden';
        document.body.appendChild(container);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.closeModal();
            }
        });
    }

    /**
     * Show confirmation modal
     * @param {Object} options - Modal options
     * @returns {Promise<boolean>} User confirmation
     */
    showConfirmation(options = {}) {
        const {
            title = 'Confirm Action',
            message = 'Are you sure you want to proceed?',
            confirmText = 'Confirm',
            cancelText = 'Cancel',
            type = 'warning' // warning, danger, info
        } = options;

        return new Promise((resolve) => {
            const modal = this.createConfirmationModal({
                title,
                message,
                confirmText,
                cancelText,
                type,
                onConfirm: () => {
                    this.closeModal();
                    resolve(true);
                },
                onCancel: () => {
                    this.closeModal();
                    resolve(false);
                }
            });

            this.showModal(modal);
        });
    }

    /**
     * Show info modal
     * @param {Object} options - Modal options
     */
    showInfo(options = {}) {
        const {
            title = 'Information',
            message = '',
            okText = 'OK'
        } = options;

        return new Promise((resolve) => {
            const modal = this.createInfoModal({
                title,
                message,
                okText,
                onOk: () => {
                    this.closeModal();
                    resolve();
                }
            });

            this.showModal(modal);
        });
    }

    /**
     * Show worker configuration modal
     * @returns {Promise<Object|null>} Worker configuration or null if cancelled
     */
    showWorkerConfig() {
        return new Promise((resolve) => {
            const modal = this.createWorkerConfigModal({
                onSave: (config) => {
                    this.closeModal();
                    resolve(config);
                },
                onCancel: () => {
                    this.closeModal();
                    resolve(null);
                }
            });

            this.showModal(modal);
        });
    }

    /**
     * Create confirmation modal
     * @param {Object} options - Modal options
     * @returns {HTMLElement} Modal element
     */
    createConfirmationModal(options) {
        const { title, message, confirmText, cancelText, type, onConfirm, onCancel } = options;
        
        const iconClass = {
            warning: 'text-yellow-600',
            danger: 'text-red-600',
            info: 'text-blue-600'
        }[type] || 'text-yellow-600';

        const iconName = {
            warning: 'warning',
            danger: 'error',
            info: 'info'
        }[type] || 'warning';

        const confirmButtonClass = {
            warning: 'bg-yellow-600 hover:bg-yellow-700',
            danger: 'bg-red-600 hover:bg-red-700',
            info: 'bg-blue-600 hover:bg-blue-700'
        }[type] || 'bg-yellow-600 hover:bg-yellow-700';

        const modal = document.createElement('div');
        modal.innerHTML = `
            <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full">
                    <div class="p-6">
                        <div class="flex items-center mb-4">
                            <span class="material-icons text-3xl ${iconClass} mr-3">${iconName}</span>
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">${title}</h3>
                        </div>
                        <p class="text-gray-600 dark:text-gray-300 mb-6">${message}</p>
                        <div class="flex space-x-3 justify-end">
                            <button class="cancel-btn px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors">
                                ${cancelText}
                            </button>
                            <button class="confirm-btn px-4 py-2 text-white ${confirmButtonClass} rounded-lg transition-colors">
                                ${confirmText}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        modal.querySelector('.confirm-btn').addEventListener('click', onConfirm);
        modal.querySelector('.cancel-btn').addEventListener('click', onCancel);
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal.firstElementChild) {
                onCancel();
            }
        });

        return modal;
    }

    /**
     * Create info modal
     * @param {Object} options - Modal options
     * @returns {HTMLElement} Modal element
     */
    createInfoModal(options) {
        const { title, message, okText, onOk } = options;

        const modal = document.createElement('div');
        modal.innerHTML = `
            <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full">
                    <div class="p-6">
                        <div class="flex items-center mb-4">
                            <span class="material-icons text-3xl text-blue-600 mr-3">info</span>
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">${title}</h3>
                        </div>
                        <div class="text-gray-600 dark:text-gray-300 mb-6">${message}</div>
                        <div class="flex justify-end">
                            <button class="ok-btn px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
                                ${okText}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        modal.querySelector('.ok-btn').addEventListener('click', onOk);
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal.firstElementChild) {
                onOk();
            }
        });

        return modal;
    }

    /**
     * Create worker configuration modal
     * @param {Object} options - Modal options
     * @returns {HTMLElement} Modal element
     */
    createWorkerConfigModal(options) {
        const { onSave, onCancel } = options;

        const modal = document.createElement('div');
        modal.innerHTML = `
            <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full">
                    <div class="p-6">
                        <div class="flex items-center mb-4">
                            <span class="material-icons text-3xl text-green-600 mr-3">settings</span>
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Worker Configuration</h3>
                        </div>
                        <div class="space-y-4 mb-6">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Number of Processes
                                </label>
                                <input type="number" id="modal-processes" min="1" max="10" value="1" 
                                       class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                    Recommended: 1-4 processes
                                </p>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Threads per Process
                                </label>
                                <input type="number" id="modal-threads" min="1" max="20" value="4" 
                                       class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                    Recommended: 4-16 threads
                                </p>
                            </div>
                        </div>
                        <div class="flex space-x-3 justify-end">
                            <button class="cancel-btn px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors">
                                Cancel
                            </button>
                            <button class="save-btn px-4 py-2 text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors">
                                Start Workers
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        modal.querySelector('.save-btn').addEventListener('click', () => {
            const processes = parseInt(modal.querySelector('#modal-processes').value);
            const threads = parseInt(modal.querySelector('#modal-threads').value);
            onSave({ processes, threads });
        });
        
        modal.querySelector('.cancel-btn').addEventListener('click', onCancel);
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal.firstElementChild) {
                onCancel();
            }
        });

        return modal;
    }

    /**
     * Show modal
     * @param {HTMLElement} modal - Modal element
     */
    showModal(modal) {
        const container = document.getElementById('modal-container');
        container.innerHTML = '';
        container.appendChild(modal);
        container.classList.remove('hidden');
        this.activeModal = modal;

        // Focus management
        const firstFocusable = modal.querySelector('button, input, select, textarea');
        if (firstFocusable) {
            firstFocusable.focus();
        }
    }

    /**
     * Close active modal
     */
    closeModal() {
        const container = document.getElementById('modal-container');
        container.classList.add('hidden');
        container.innerHTML = '';
        this.activeModal = null;
    }
}

// Create global modal system instance
window.modals = new ModalSystem();

// Enhanced dashboard methods using modals
if (window.dashboard) {
    // Override confirmation methods to use modals
    const originalStartWorkers = window.dashboard.startWorkers;
    window.dashboard.startWorkers = async function() {
        const config = await window.modals.showWorkerConfig();
        if (config) {
            try {
                await window.tasksAPI.startWorkers(config);
                await window.modals.showInfo({
                    title: 'Success',
                    message: `Workers started successfully with ${config.processes} processes and ${config.threads} threads per process.`
                });
                this.loadTabData(this.currentTab);
            } catch (error) {
                console.error('Failed to start workers:', error);
                await window.modals.showInfo({
                    title: 'Error',
                    message: 'Failed to start workers. Please check the logs for more details.'
                });
            }
        }
    };

    const originalStopWorkers = window.dashboard.stopWorkers;
    window.dashboard.stopWorkers = async function() {
        const confirmed = await window.modals.showConfirmation({
            title: 'Stop Workers',
            message: 'Are you sure you want to stop all workers? This will halt task processing.',
            confirmText: 'Stop Workers',
            type: 'warning'
        });

        if (confirmed) {
            try {
                await window.tasksAPI.stopWorkers();
                await window.modals.showInfo({
                    title: 'Success',
                    message: 'Workers stopped successfully.'
                });
                this.loadTabData(this.currentTab);
            } catch (error) {
                console.error('Failed to stop workers:', error);
                await window.modals.showInfo({
                    title: 'Error',
                    message: 'Failed to stop workers. Please check the logs for more details.'
                });
            }
        }
    };

    const originalClearQueues = window.dashboard.clearQueues;
    window.dashboard.clearQueues = async function() {
        const confirmed = await window.modals.showConfirmation({
            title: 'Clear All Queues',
            message: 'This will remove all pending tasks from all queues. This action cannot be undone.',
            confirmText: 'Clear Queues',
            type: 'danger'
        });

        if (confirmed) {
            try {
                await window.tasksAPI.clearQueues();
                await window.modals.showInfo({
                    title: 'Success',
                    message: 'All queues cleared successfully.'
                });
                this.loadTabData(this.currentTab);
            } catch (error) {
                console.error('Failed to clear queues:', error);
                await window.modals.showInfo({
                    title: 'Error',
                    message: 'Failed to clear queues. Please check the logs for more details.'
                });
            }
        }
    };

    const originalPurgeFailedTasks = window.dashboard.purgeFailedTasks;
    window.dashboard.purgeFailedTasks = async function() {
        const confirmed = await window.modals.showConfirmation({
            title: 'Purge Failed Tasks',
            message: 'This will permanently remove all failed tasks from the system. This action cannot be undone.',
            confirmText: 'Purge Failed Tasks',
            type: 'danger'
        });

        if (confirmed) {
            try {
                await window.tasksAPI.purgeFailedTasks();
                await window.modals.showInfo({
                    title: 'Success',
                    message: 'Failed tasks purged successfully.'
                });
                this.loadTabData(this.currentTab);
            } catch (error) {
                console.error('Failed to purge failed tasks:', error);
                await window.modals.showInfo({
                    title: 'Error',
                    message: 'Failed to purge failed tasks. Please check the logs for more details.'
                });
            }
        }
    };

    // Override simple alert methods
    window.dashboard.showSuccess = async function(message) {
        await window.modals.showInfo({
            title: 'Success',
            message: message
        });
    };

    window.dashboard.showError = async function(message) {
        await window.modals.showInfo({
            title: 'Error',
            message: message
        });
    };
}
