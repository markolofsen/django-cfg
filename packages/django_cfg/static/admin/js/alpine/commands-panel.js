/**
 * Commands Panel Alpine.js Component
 *
 * Manages command search, filtering, and category toggling
 */

function commandsPanelComponent(totalCommands) {
    return {
        searchQuery: '',
        totalCommands: totalCommands,
        visibleCommands: totalCommands,
        expandedCategories: new Set(),

        init() {
            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                // Focus search with Ctrl+F or Cmd+F
                if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                    e.preventDefault();
                    this.$refs.searchInput?.focus();
                }

                // Clear search with Escape
                if (e.key === 'Escape' && document.activeElement === this.$refs.searchInput) {
                    this.clearSearch();
                    this.$refs.searchInput?.blur();
                }
            });
        },

        search() {
            const query = this.searchQuery.toLowerCase().trim();
            let visibleCount = 0;

            // Get all categories
            const categories = document.querySelectorAll('[id^="content-"]');

            categories.forEach(category => {
                const categoryName = category.id.replace('content-', '');
                const commands = category.querySelectorAll('.command-item');
                let categoryHasVisibleCommands = false;

                commands.forEach(command => {
                    const commandName = command.querySelector('.command-name')?.textContent.toLowerCase() || '';
                    const commandDesc = command.querySelector('.command-description')?.textContent.toLowerCase() || '';

                    if (!query || commandName.includes(query) || commandDesc.includes(query)) {
                        command.style.display = 'block';
                        categoryHasVisibleCommands = true;
                        visibleCount++;
                    } else {
                        command.style.display = 'none';
                    }
                });

                // Show/hide category based on whether it has visible commands
                const categoryHeader = document.querySelector(`button[data-category="${categoryName}"]`);
                const categoryContainer = categoryHeader?.parentElement;

                if (categoryContainer) {
                    if (categoryHasVisibleCommands) {
                        categoryContainer.style.display = 'block';

                        // Auto-expand categories when searching
                        if (query) {
                            this.expandedCategories.add(categoryName);
                        }
                    } else {
                        categoryContainer.style.display = 'none';
                    }
                }
            });

            this.visibleCommands = visibleCount;
        },

        clearSearch() {
            this.searchQuery = '';
            this.visibleCommands = this.totalCommands;

            // Show all commands and categories
            const categories = document.querySelectorAll('[id^="content-"]');
            const allCommands = document.querySelectorAll('.command-item');

            categories.forEach(category => {
                const categoryName = category.id.replace('content-', '');
                const categoryHeader = document.querySelector(`button[data-category="${categoryName}"]`);
                const categoryContainer = categoryHeader?.parentElement;

                if (categoryContainer) {
                    categoryContainer.style.display = 'block';
                }

                // Collapse all categories
                this.expandedCategories.delete(categoryName);
            });

            allCommands.forEach(command => {
                command.style.display = 'block';
            });
        },

        toggleCategory(categoryName) {
            if (this.expandedCategories.has(categoryName)) {
                this.expandedCategories.delete(categoryName);
            } else {
                this.expandedCategories.add(categoryName);
            }
        },

        isCategoryExpanded(categoryName) {
            return this.expandedCategories.has(categoryName);
        },

        get showNoResults() {
            return this.visibleCommands === 0 && this.searchQuery.trim() !== '';
        },

        get showClearButton() {
            return this.searchQuery.trim() !== '';
        }
    };
}

// Register component when Alpine initializes
document.addEventListener('alpine:init', () => {
    Alpine.data('commandsPanel', commandsPanelComponent);
});

// Global wrapper for backward compatibility
window.toggleCategory = function(category) {
    const panel = document.querySelector('[x-data*="commandsPanel"]');
    if (panel && Alpine) {
        const component = Alpine.$data(panel);
        if (component && component.toggleCategory) {
            component.toggleCategory(category);
        }
    }
};
