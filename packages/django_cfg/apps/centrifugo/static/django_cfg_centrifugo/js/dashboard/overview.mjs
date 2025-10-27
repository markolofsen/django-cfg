/**
 * Centrifugo Overview Dashboard Module
 * Handles overview, publishes, and channels tabs
 */
export class OverviewModule {
    constructor(api, dashboard) {
        this.api = api;
        this.dashboard = dashboard;
        this.charts = {};
    }

    async loadData(tabName) {
        switch (tabName) {
            case 'overview':
                await this.loadOverviewCharts();
                break;
            case 'publishes':
                await this.loadRecentPublishes();
                break;
            case 'channels':
                await this.loadChannelStats();
                break;
        }
    }

    async loadOverviewStats() {
        try {
            const stats = await this.api.centrifugoAdminApiMonitorOverviewRetrieve({ hours: 24 });

            if (stats) {
                this.updateElement('total-publishes', stats.total || 0);
                this.updateElement('avg-duration', (stats.avg_duration_ms || 0).toFixed(0));
                this.updateElement('failed-count', stats.failed || 0);

                const successRate = stats.success_rate || 0;
                const successRateElement = document.getElementById('success-rate-value');
                if (successRateElement) {
                    const rateSpan = successRateElement.querySelector('span');
                    if (rateSpan) {
                        rateSpan.textContent = successRate.toFixed(1);
                        rateSpan.className = this.getSuccessRateClass(successRate);
                    }
                }

                // Note: trend is not provided by API, remove if UI expects it
                const trendElement = document.getElementById('publish-trend');
                if (trendElement) {
                    trendElement.style.display = 'none'; // hide trend since API doesn't provide it
                }
            }
        } catch (error) {
            console.error('Error loading overview stats:', error);
        }
    }

    async loadOverviewCharts() {
        try {
            console.log('📊 Loading overview charts...');
            const stats = await this.api.centrifugoAdminApiMonitorOverviewRetrieve({ hours: 24 });

            console.log('📊 Overview stats:', stats);
            if (stats) {
                // Render both charts with current stats
                this.renderTimelinePlaceholder(stats);
                this.renderBreakdownChart(stats);
                this.updateAckStats(stats);
            }
        } catch (error) {
            console.error('Error loading overview charts:', error);
        }
    }

    renderTimelinePlaceholder(stats) {
        const canvas = document.getElementById('publish-timeline-chart');
        if (!canvas) return;

        const hasData = stats.total > 0;

        // If no data, show text message instead of empty chart
        if (!hasData) {
            const parent = canvas.parentElement;
            parent.innerHTML = `
                <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                    <span class="material-icons mr-2 text-purple-500">timeline</span>
                    Publish Timeline (24h)
                </h3>
                <div class="flex items-center justify-center h-[200px] bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div class="text-center">
                        <span class="material-icons text-6xl text-gray-300 dark:text-gray-600 mb-2">show_chart</span>
                        <p class="text-gray-500 dark:text-gray-400">No publish data yet</p>
                        <p class="text-sm text-gray-400 dark:text-gray-500">Try running a Quick Test Scenario</p>
                    </div>
                </div>
            `;
            return;
        }

        const ctx = canvas.getContext('2d');

        if (this.charts.timeline) {
            this.charts.timeline.destroy();
        }

        console.log('📊 Rendering timeline chart:', { total: stats.total, hasData });

        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Now'],
                datasets: [{
                    label: 'Publishes',
                    data: [stats.total],
                    borderColor: 'rgb(168, 85, 247)',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    renderTimelineChart(timeline) {
        const canvas = document.getElementById('publish-timeline-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        if (this.charts.timeline) {
            this.charts.timeline.destroy();
        }

        const labels = timeline.map(t => new Date(t.timestamp).toLocaleTimeString());
        const data = timeline.map(t => t.count);

        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Publishes',
                    data: data,
                    borderColor: 'rgb(168, 85, 247)',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    renderBreakdownChart(stats) {
        const canvas = document.getElementById('status-breakdown-chart');
        if (!canvas) return;

        const success = stats.successful || 0;
        const failed = stats.failed || 0;
        const timeout = stats.timeout || 0;
        const hasData = success + failed + timeout > 0;

        // If no data, show text message instead of empty chart
        if (!hasData) {
            const parent = canvas.parentElement;
            parent.innerHTML = `
                <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                    <span class="material-icons mr-2 text-purple-500">pie_chart</span>
                    Success/Failure Breakdown
                </h3>
                <div class="flex items-center justify-center h-[200px] bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div class="text-center">
                        <span class="material-icons text-6xl text-gray-300 dark:text-gray-600 mb-2">pie_chart</span>
                        <p class="text-gray-500 dark:text-gray-400">No status data yet</p>
                        <p class="text-sm text-gray-400 dark:text-gray-500">Publish messages to see breakdown</p>
                    </div>
                </div>
            `;
            return;
        }

        const ctx = canvas.getContext('2d');

        if (this.charts.breakdown) {
            this.charts.breakdown.destroy();
        }

        console.log('📊 Rendering breakdown chart:', { success, failed, timeout, hasData });

        this.charts.breakdown = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Success', 'Failed', 'Timeout'],
                datasets: [{
                    data: [success, failed, timeout],
                    backgroundColor: [
                        'rgb(34, 197, 94)',
                        'rgb(239, 68, 68)',
                        'rgb(245, 158, 11)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        return {
                                            text: `${label}: ${value}`,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            hidden: false,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    }
                }
            }
        });
    }

    updateAckStats(stats) {
        // API returns avg_acks_received directly, not nested in ack_stats
        this.updateElement('avg-acks', (stats.avg_acks_received || 0).toFixed(1));

        // Calculate total ACKs if we need to display it (not in API response)
        const totalAcks = Math.round((stats.total || 0) * (stats.avg_acks_received || 0));
        this.updateElement('total-acks', totalAcks);

        // ACK tracking rate not provided by API - could be calculated from publishes data
        // For now, hide or use a placeholder
        const ackRateElement = document.getElementById('ack-rate');
        if (ackRateElement && ackRateElement.parentElement) {
            ackRateElement.parentElement.style.display = 'none';
        }
    }

    async loadRecentPublishes() {
        try {
            const channelFilter = document.getElementById('publish-channel-filter')?.value || '';
            // Note: status filtering is done client-side since API doesn't support it
            const statusFilter = document.getElementById('publish-status-filter')?.value || '';

            const params = { count: 50 };
            if (channelFilter) {
                params.channel = channelFilter;
            }

            const data = await this.api.centrifugoAdminApiMonitorPublishesRetrieve(params);

            if (data) {
                let publishes = data.publishes || [];

                // Apply client-side status filter if selected
                if (statusFilter) {
                    publishes = publishes.filter(pub => pub.status === statusFilter);
                }

                this.renderPublishesTable(publishes);
                this.updateElement('publishes-showing', publishes.length);

                const channels = data.available_channels || [];
                this.updateChannelFilter(channels);
            }
        } catch (error) {
            console.error('Error loading recent publishes:', error);
        }
    }

    renderPublishesTable(publishes) {
        const tbody = document.getElementById('publishes-table-body');
        if (!tbody) return;

        if (publishes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">No publishes found</td></tr>';
            return;
        }

        let html = '';
        publishes.forEach(pub => {
            const statusClass = this.getStatusBadgeClass(pub.status);
            // API returns: acks_received, acks_expected (not expected_acks)
            const ackText = pub.acks_expected > 0 ? pub.acks_received + '/' + pub.acks_expected : 'N/A';

            html += '<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">';
            // API returns: created_at (not timestamp)
            html += '<td class="px-4 py-3 text-sm">' + this.formatTimestamp(pub.created_at) + '</td>';
            html += '<td class="px-4 py-3 text-xs font-mono">' + this.escapeHtml((pub.message_id || '').substring(0, 12)) + '...</td>';
            html += '<td class="px-4 py-3"><code class="text-sm bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">' + this.escapeHtml(pub.channel) + '</code></td>';
            html += '<td class="px-4 py-3"><span class="status-badge ' + statusClass + '">' + this.escapeHtml(pub.status) + '</span></td>';
            html += '<td class="px-4 py-3 text-sm">' + ackText + '</td>';
            html += '<td class="px-4 py-3 text-sm">' + (pub.duration_ms || 0).toFixed(0) + 'ms</td>';
            html += '</tr>';
        });

        tbody.innerHTML = html;
    }

    updateChannelFilter(channels) {
        const select = document.getElementById('publish-channel-filter');
        if (!select) return;

        const currentValue = select.value;
        let html = '<option value="">All Channels</option>';
        channels.forEach(channel => {
            html += '<option value="' + this.escapeHtml(channel) + '">' + this.escapeHtml(channel) + '</option>';
        });
        select.innerHTML = html;
        select.value = currentValue;
    }

    async loadChannelStats() {
        try {
            const data = await this.api.centrifugoAdminApiMonitorChannelsRetrieve({ hours: 24 });

            if (data) {
                const channels = data.channels || [];
                this.renderChannelsTable(channels);
            }
        } catch (error) {
            console.error('Error loading channel stats:', error);
        }
    }

    renderChannelsTable(channels) {
        const tbody = document.getElementById('channels-table-body');
        if (!tbody) return;

        if (channels.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">No channel data available</td></tr>';
            return;
        }

        let html = '';
        channels.forEach(channel => {
            // API returns: total, successful, failed (not success_rate)
            // Calculate success rate client-side
            const total = channel.total || 0;
            const successful = channel.successful || 0;
            const successRate = total > 0 ? (successful / total) * 100 : 0;
            const successClass = this.getSuccessRateClass(successRate);

            html += '<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">';
            html += '<td class="px-4 py-3"><code class="text-sm bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">' + this.escapeHtml(channel.channel) + '</code></td>';
            html += '<td class="px-4 py-3 text-sm font-medium">' + total + '</td>';
            html += '<td class="px-4 py-3 text-sm"><span class="' + successClass + '">' + successRate.toFixed(1) + '%</span></td>';
            html += '<td class="px-4 py-3 text-sm">' + (channel.avg_duration_ms || 0).toFixed(0) + 'ms</td>';
            html += '<td class="px-4 py-3 text-sm">' + (channel.avg_acks || 0).toFixed(1) + '</td>';
            // API doesn't provide last_activity, remove this column or use a placeholder
            html += '<td class="px-4 py-3 text-sm text-gray-400">N/A</td>';
            html += '</tr>';
        });

        tbody.innerHTML = html;
    }

    getStatusBadgeClass(status) {
        switch (status) {
            case 'success':
                return 'success';
            case 'failed':
                return 'failed';
            case 'timeout':
                return 'timeout';
            default:
                return '';
        }
    }

    getSuccessRateClass(rate) {
        if (rate >= 95) return 'success-rate-high';
        if (rate >= 80) return 'success-rate-medium';
        return 'success-rate-low';
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    formatTimestamp(isoString) {
        try {
            const date = new Date(isoString);
            return date.toLocaleTimeString();
        } catch {
            return 'N/A';
        }
    }

    escapeHtml(unsafe) {
        const div = document.createElement('div');
        div.textContent = unsafe;
        return div.innerHTML;
    }
}
