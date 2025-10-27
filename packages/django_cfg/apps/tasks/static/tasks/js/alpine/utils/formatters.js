/**
 * Formatting Utilities
 */

export function formatDuration(ms) {
    if (!ms) return '-';

    if (ms < 1000) {
        return `${ms}ms`;
    } else if (ms < 60000) {
        return `${(ms / 1000).toFixed(1)}s`;
    } else {
        return `${(ms / 60000).toFixed(1)}m`;
    }
}

export function formatDate(dateString) {
    if (!dateString) return '-';

    try {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch (error) {
        return dateString;
    }
}

export function getStatusColor(status) {
    const colors = {
        'pending': 'yellow',
        'running': 'blue',
        'completed': 'green',
        'failed': 'red'
    };
    return colors[status] || 'gray';
}
