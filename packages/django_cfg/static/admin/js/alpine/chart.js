/**
 * Chart Alpine.js Component
 *
 * Universal Chart.js wrapper for Alpine
 */

function chartComponent(chartData, chartType = 'line', options = {}) {
    return {
        chart: null,
        chartData: chartData,
        chartType: chartType,

        init() {
            this.$nextTick(() => {
                this.renderChart();
            });
        },

        renderChart() {
            const canvas = this.$refs.canvas;

            if (!canvas || typeof Chart === 'undefined') {
                console.error('Chart.js not loaded or canvas not found');
                return;
            }

            try {
                // Default options
                const defaultOptions = {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                };

                // Merge with custom options
                const mergedOptions = this.deepMerge(defaultOptions, options);

                this.chart = new Chart(canvas, {
                    type: this.chartType,
                    data: this.chartData,
                    options: mergedOptions
                });
            } catch (error) {
                console.error('Error creating chart:', error);
            }
        },

        updateChart(newData) {
            if (this.chart) {
                this.chart.data = newData;
                this.chart.update();
            }
        },

        destroy() {
            if (this.chart) {
                this.chart.destroy();
                this.chart = null;
            }
        },

        deepMerge(target, source) {
            const output = Object.assign({}, target);
            if (this.isObject(target) && this.isObject(source)) {
                Object.keys(source).forEach(key => {
                    if (this.isObject(source[key])) {
                        if (!(key in target))
                            Object.assign(output, { [key]: source[key] });
                        else
                            output[key] = this.deepMerge(target[key], source[key]);
                    } else {
                        Object.assign(output, { [key]: source[key] });
                    }
                });
            }
            return output;
        },

        isObject(item) {
            return item && typeof item === 'object' && !Array.isArray(item);
        }
    };
}

// Register component
document.addEventListener('alpine:init', () => {
    Alpine.data('chart', chartComponent);
});
