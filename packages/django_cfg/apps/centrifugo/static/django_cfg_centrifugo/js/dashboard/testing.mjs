/**
 * Centrifugo Usage Guide Module
 * Handles usage guide tab functionality (read-only, no publish capabilities)
 */
export class UsageGuideModule {
    constructor(api, dashboard) {
        this.api = api;
        this.dashboard = dashboard;
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Apply filters button for publishes table (if exists in other tabs)
        const applyFiltersBtn = document.getElementById('apply-publish-filters');
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => {
                this.dashboard.overviewModule.loadRecentPublishes();
            });
        }

        // No publish functionality - this is a read-only guide
        console.log('Usage Guide Module initialized (read-only)');
    }

    escapeHtml(unsafe) {
        const div = document.createElement('div');
        div.textContent = unsafe;
        return div.innerHTML;
    }
}
