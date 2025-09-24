/**
 * Notification System
 * Handles toast notifications and alerts
 */

class NotificationManager {
    constructor() {
        this.container = document.getElementById('notification-container');
        this.notifications = new Map();
        this.nextId = 1;
    }

    /**
     * Show a notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, warning, info)
     * @param {number} duration - Auto-dismiss duration in ms (0 = no auto-dismiss)
     * @returns {number} Notification ID
     */
    show(message, type = 'info', duration = 5000) {
        const id = this.nextId++;
        const notification = this.createNotification(id, message, type);
        
        this.container.appendChild(notification);
        this.notifications.set(id, notification);
        
        // Animate in
        requestAnimationFrame(() => {
            notification.classList.remove('opacity-0', 'translate-y-2');
            notification.classList.add('opacity-100', 'translate-y-0');
        });
        
        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => this.dismiss(id), duration);
        }
        
        return id;
    }

    /**
     * Dismiss a notification
     * @param {number} id - Notification ID
     */
    dismiss(id) {
        const notification = this.notifications.get(id);
        if (!notification) return;
        
        // Animate out
        notification.classList.remove('opacity-100', 'translate-y-0');
        notification.classList.add('opacity-0', 'translate-y-2');
        
        // Remove from DOM after animation
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            this.notifications.delete(id);
        }, 300);
    }

    /**
     * Create notification element
     * @param {number} id - Notification ID
     * @param {string} message - Message text
     * @param {string} type - Notification type
     * @returns {HTMLElement} Notification element
     */
    createNotification(id, message, type) {
        const notification = document.createElement('div');
        notification.className = `
            max-w-sm w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg pointer-events-auto 
            ring-1 ring-black ring-opacity-5 overflow-hidden transform transition-all duration-300 
            opacity-0 translate-y-2
        `.trim();
        
        const colors = {
            success: 'text-green-600 dark:text-green-400',
            error: 'text-red-600 dark:text-red-400',
            warning: 'text-yellow-600 dark:text-yellow-400',
            info: 'text-blue-600 dark:text-blue-400'
        };
        
        const icons = {
            success: 'check_circle',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };
        
        notification.innerHTML = `
            <div class="p-4">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <span class="material-icons ${colors[type] || colors.info}">${icons[type] || icons.info}</span>
                    </div>
                    <div class="ml-3 w-0 flex-1 pt-0.5">
                        <p class="text-sm font-medium text-gray-900 dark:text-white">${message}</p>
                    </div>
                    <div class="ml-4 flex-shrink-0 flex">
                        <button class="bg-white dark:bg-gray-800 rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500" 
                                onclick="window.notifications.dismiss(${id})">
                            <span class="sr-only">Close</span>
                            <span class="material-icons text-sm">close</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return notification;
    }

    /**
     * Convenience methods
     */
    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 8000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }

    /**
     * Clear all notifications
     */
    clear() {
        this.notifications.forEach((_, id) => this.dismiss(id));
    }
}

// Initialize notification manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.notifications = new NotificationManager();
});
