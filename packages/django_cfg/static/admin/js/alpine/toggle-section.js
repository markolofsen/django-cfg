/**
 * Toggle Section Alpine.js Component
 *
 * Simple collapsible section toggle
 */

function toggleSectionComponent() {
    return {
        expandedSections: new Set(),

        toggleSection(sectionId) {
            if (this.expandedSections.has(sectionId)) {
                this.expandedSections.delete(sectionId);
            } else {
                this.expandedSections.add(sectionId);
            }
        },

        isSectionExpanded(sectionId) {
            return this.expandedSections.has(sectionId);
        }
    };
}

// Register component
document.addEventListener('alpine:init', () => {
    Alpine.data('toggleSection', toggleSectionComponent);
});
