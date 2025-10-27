/**
 * Activity Tracker Alpine.js Component
 *
 * GitHub-style heatmap visualization for activity data
 */

function activityTrackerComponent(activityData) {
    return {
        activityData: activityData || [],
        weeks: [],

        init() {
            this.processData();
        },

        processData() {
            if (!this.activityData || this.activityData.length === 0) {
                return;
            }

            // Group days into weeks (7 days per column)
            this.weeks = [];
            for (let i = 0; i < this.activityData.length; i += 7) {
                this.weeks.push(this.activityData.slice(i, i + 7));
            }
        },

        getCellColor(count) {
            if (count === 0) {
                return 'bg-gray-200 dark:bg-gray-700';
            } else if (count <= 2) {
                return 'bg-green-200 dark:bg-green-800';
            } else if (count <= 5) {
                return 'bg-green-400 dark:bg-green-600';
            } else if (count <= 10) {
                return 'bg-green-600 dark:bg-green-500';
            } else {
                return 'bg-green-800 dark:bg-green-400';
            }
        },

        getCellTitle(day) {
            return `${day.date}: ${day.count} activities`;
        },

        get hasData() {
            return this.activityData && this.activityData.length > 0;
        }
    };
}

// Register component
document.addEventListener('alpine:init', () => {
    Alpine.data('activityTracker', activityTrackerComponent);
});
