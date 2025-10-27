/**
 * System Metrics Alpine.js Component
 *
 * Provides reactive width styling for health percentage bars
 */

function systemMetricsComponent(metricsData) {
    return {
        metrics: metricsData || {},

        getBarStyle(percentage) {
            return `width: ${percentage}%`;
        }
    };
}

// Register component
document.addEventListener('alpine:init', () => {
    Alpine.data('systemMetrics', systemMetricsComponent);
});
