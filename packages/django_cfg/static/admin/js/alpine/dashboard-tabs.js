/**
 * Dashboard Tabs Alpine.js Component
 *
 * Manages dashboard tabs with URL hash navigation and browser history
 */

function dashboardTabsComponent() {
    return {
        activeTab: 0,
        tabNames: ['overview', 'zones', 'users', 'system', 'stats', 'app-stats', 'commands', 'widgets'],

        init() {
            // Initialize from URL hash or default to first tab
            this.activeTab = this.getTabFromHash();

            // Handle browser back/forward buttons
            window.addEventListener('hashchange', () => {
                this.activeTab = this.getTabFromHash();
            });
        },

        switchTab(index) {
            this.activeTab = index;

            // Update URL hash
            if (this.tabNames[index]) {
                history.replaceState(null, null, '#' + this.tabNames[index]);
            }
        },

        getTabFromHash() {
            const hash = window.location.hash.substring(1); // Remove #
            const tabIndex = this.tabNames.indexOf(hash);
            return tabIndex >= 0 ? tabIndex : 0; // Default to first tab
        },

        isActive(index) {
            return this.activeTab === index;
        }
    };
}

// Register component when Alpine initializes
document.addEventListener('alpine:init', () => {
    Alpine.data('dashboardTabs', dashboardTabsComponent);
});
