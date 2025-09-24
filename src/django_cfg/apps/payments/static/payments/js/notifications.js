/**
 * Notification System for Payment Dashboard
 * Handles toast notifications with auto-dismiss and styling
 */

class NotificationManager {
    constructor() {
        this.container = this.getOrCreateContainer();
        this.notifications = new Map();
        this.defaultDuration = 5000; // 5 seconds
    }

    getOrCreateContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 z-50 space-y-2';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', options = {}) {
        const id = this.generateId();
        const duration = options.duration || this.defaultDuration;
        const persistent = options.persistent || false;

        const notification = this.createNotificationElement(id, message, type, persistent);
        this.container.appendChild(notification);
        this.notifications.set(id, notification);

        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('animate-in');
        });

        // Auto-dismiss if not persistent
        if (!persistent) {
            setTimeout(() => {
                this.dismiss(id);
            }, duration);
        }

        return id;
    }

    createNotificationElement(id, message, type, persistent) {
        const notification = document.createElement('div');
        notification.id = `notification-${id}`;
        notification.className = `notification ${type} transform transition-all duration-300 translate-y-2 opacity-0`;
        
        const typeIcons = {
            success: 'check_circle',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };

        const typeColors = {
            success: 'text-green-600',
            error: 'text-red-600',
            warning: 'text-yellow-600',
            info: 'text-blue-600'
        };

        notification.innerHTML = `
            <div class="p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <span class="material-icons ${typeColors[type]}">${typeIcons[type]}</span>
                    </div>
                    <div class="ml-3 w-0 flex-1">
                        <p class="text-sm font-medium text-gray-900 dark:text-white">
                            ${this.escapeHtml(message)}
                        </p>
                    </div>
                    ${!persistent ? `
                    <div class="ml-4 flex-shrink-0 flex">
                        <button class="dismiss-btn bg-white dark:bg-gray-800 rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" onclick="window.notificationManager.dismiss('${id}')">
                            <span class="sr-only">Close</span>
                            <span class="material-icons text-sm">close</span>
                        </button>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;

        // Add CSS class for animation
        notification.style.setProperty('--tw-translate-y', '0.5rem');
        
        return notification;
    }

    dismiss(id) {
        const notification = this.notifications.get(id);
        if (!notification) return;

        // Animate out
        notification.classList.add('animate-out');
        notification.style.setProperty('--tw-translate-y', '-0.5rem');
        notification.style.opacity = '0';

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            this.notifications.delete(id);
        }, 300);
    }

    dismissAll() {
        this.notifications.forEach((notification, id) => {
            this.dismiss(id);
        });
    }

    // Convenience methods
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    error(message, options = {}) {
        return this.show(message, 'error', options);
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    // Payment-specific notifications
    paymentCreated(paymentId) {
        return this.success(`Payment #${paymentId} created successfully`);
    }

    paymentCompleted(paymentId) {
        return this.success(`Payment #${paymentId} completed!`);
    }

    paymentFailed(paymentId, reason = '') {
        const message = `Payment #${paymentId} failed${reason ? ': ' + reason : ''}`;
        return this.error(message);
    }

    paymentCancelled(paymentId) {
        return this.warning(`Payment #${paymentId} cancelled`);
    }

    connectionStatus(connected) {
        if (connected) {
            return this.success('Connected to payment system', { duration: 3000 });
        } else {
            return this.error('Connection lost', { persistent: true });
        }
    }

    // Utility methods
    generateId() {
        return Math.random().toString(36).substr(2, 9);
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    .notification.animate-in {
        transform: translateY(0);
        opacity: 1;
    }
    
    .notification.animate-out {
        transform: translateY(-0.5rem);
        opacity: 0;
    }
`;
document.head.appendChild(style);

// Initialize notification manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = new NotificationManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationManager;
}
