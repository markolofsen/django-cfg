/**
 * TabManager - Handles tab switching and navigation
 */
export class TabManager {
    constructor() {
        this.currentTab = 'overview';
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = e.currentTarget.dataset.tab;
                this.switchTab(tabId);
            });
        });
    }

    /**
     * Switch to a specific tab
     * @param {string} tabId - Tab identifier
     */
    switchTab(tabId) {
        // Update active tab styling
        document.querySelectorAll('.tab-button').forEach(tab => {
            tab.classList.remove('active', 'border-primary-500', 'text-primary-600', 'dark:text-primary-400');
            tab.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300', 'dark:text-gray-400', 'dark:hover:text-gray-300');
        });

        // Add active to selected tab
        const activeTab = document.querySelector(`[data-tab="${tabId}"]`);
        if (activeTab) {
            activeTab.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300', 'dark:text-gray-400', 'dark:hover:text-gray-300');
            activeTab.classList.add('active', 'border-primary-500', 'text-primary-600', 'dark:text-primary-400');
        }

        // Hide all tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.add('hidden');
            panel.classList.remove('active');
        });

        // Show selected tab panel
        const activePanel = document.querySelector(`#${tabId}-tab`);
        if (activePanel) {
            activePanel.classList.remove('hidden');
            activePanel.classList.add('active');
        }

        this.currentTab = tabId;
        
        // Trigger tab change event
        this.onTabChange(tabId);
    }

    /**
     * Get current active tab
     * @returns {string} - Current tab ID
     */
    getCurrentTab() {
        return this.currentTab;
    }

    /**
     * Tab change callback - override in dashboard
     * @param {string} tabId - New tab ID
     */
    onTabChange(tabId) {
        // Override this method in the main dashboard
        console.log('Tab changed to:', tabId);
    }

    /**
     * Update tab badge count
     * @param {string} tabId - Tab identifier
     * @param {number} count - Badge count
     */
    updateTabBadge(tabId, count) {
        const badge = document.querySelector(`#${tabId}-count-badge`);
        if (badge) {
            badge.textContent = count;
        }
    }
}
