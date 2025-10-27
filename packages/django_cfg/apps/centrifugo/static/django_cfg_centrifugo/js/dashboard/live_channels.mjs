/**
 * Live Channels Module
 * Handles real-time channel monitoring from Centrifugo server
 */
export class LiveChannelsModule {
    constructor(api, dashboard) {
        this.api = api;
        this.dashboard = dashboard;
        this.currentChannel = null;
    }

    async loadLiveChannels() {
        try {
            console.log('Loading live channels from Centrifugo server...');

            const patternInput = document.getElementById('live-channel-pattern');
            const pattern = patternInput ? patternInput.value.trim() : '';

            // Call Centrifugo channels API
            const data = { pattern: pattern || '' };
            const response = await this.api.centrifugoAdminApiServerChannelsCreate(data);

            if (response && response.result) {
                const channels = response.result.channels || {};
                this.renderChannelsGrid(channels);
                this.updateLiveChannelsBadge(Object.keys(channels).length);
            } else if (response && response.error) {
                console.error('Centrifugo API error:', response.error);
                this.showError('Failed to load channels: ' + response.error.message);
            }
        } catch (error) {
            console.error('Error loading live channels:', error);
            this.showError('Failed to connect to Centrifugo server');
        }
    }

    renderChannelsGrid(channels) {
        const grid = document.getElementById('live-channels-grid');
        const emptyState = document.getElementById('live-channels-empty');

        if (!grid) return;

        const channelEntries = Object.entries(channels);

        if (channelEntries.length === 0) {
            grid.innerHTML = '';
            if (emptyState) emptyState.classList.remove('hidden');
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');

        let html = '';
        channelEntries.forEach(([channelName, info]) => {
            const numClients = info.num_clients || 0;
            const statusColor = numClients > 0 ? 'text-green-500' : 'text-gray-400';
            const statusIcon = numClients > 0 ? 'radio_button_checked' : 'radio_button_unchecked';

            html += `
                <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:border-purple-500 dark:hover:border-purple-400 transition-colors">
                    <!-- Channel Header -->
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex items-center gap-2 min-w-0 flex-1">
                            <span class="material-icons ${statusColor}">${statusIcon}</span>
                            <code class="text-sm font-mono text-gray-900 dark:text-white truncate">${this.escapeHtml(channelName)}</code>
                        </div>
                    </div>

                    <!-- Stats -->
                    <div class="grid grid-cols-2 gap-3 mb-3">
                        <div>
                            <p class="text-xs text-gray-600 dark:text-gray-400">Clients</p>
                            <p class="text-xl font-bold text-purple-600 dark:text-purple-400">${numClients}</p>
                        </div>
                        <div>
                            <p class="text-xs text-gray-600 dark:text-gray-400">Status</p>
                            <p class="text-sm font-medium ${numClients > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'}">
                                ${numClients > 0 ? 'Active' : 'Idle'}
                            </p>
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="flex gap-2">
                        <button onclick="window.centrifugoDashboard.liveChannelsModule.viewChannelDetails('${this.escapeHtml(channelName)}')"
                                class="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm font-medium flex items-center justify-center gap-1">
                            <span class="material-icons text-base">visibility</span>
                            View Details
                        </button>
                    </div>
                </div>
            `;
        });

        grid.innerHTML = html;
    }

    async viewChannelDetails(channel) {
        this.currentChannel = channel;
        const modal = document.getElementById('channel-details-modal');
        if (!modal) return;

        // Show modal
        modal.classList.remove('hidden');

        // Set channel name
        const modalTitle = document.getElementById('modal-channel-name');
        if (modalTitle) {
            modalTitle.textContent = channel;
        }

        // Load presence and history
        await this.loadChannelPresence(channel);
        await this.loadChannelHistory(channel);
        await this.loadPresenceStats(channel);
    }

    async loadPresenceStats(channel) {
        try {
            const data = { channel };
            const response = await this.api.centrifugoAdminApiServerPresenceStatsCreate(data);

            if (response && response.error) {
                // Feature not available (e.g., code 108)
                console.warn('Presence stats not available:', response.error.message);
                this.updateElement('modal-clients-count', 'N/A');
                this.updateElement('modal-users-count', 'N/A');
            } else if (response && response.result) {
                const stats = response.result;
                this.updateElement('modal-clients-count', stats.num_clients || 0);
                this.updateElement('modal-users-count', stats.num_users || 0);
            }
        } catch (error) {
            console.error('Error loading presence stats:', error);
            this.updateElement('modal-clients-count', 'Error');
            this.updateElement('modal-users-count', 'Error');
        }
    }

    async loadChannelPresence(channel) {
        try {
            const data = { channel };
            const response = await this.api.centrifugoAdminApiServerPresenceCreate(data);

            if (response && response.error) {
                // Feature not available (e.g., code 108)
                console.warn('Presence not available:', response.error.message);
                this.renderPresenceList({}, 'Presence tracking not enabled for this channel');
            } else if (response && response.result) {
                const presence = response.result.presence || {};
                this.renderPresenceList(presence);
            }
        } catch (error) {
            console.error('Error loading channel presence:', error);
            this.renderPresenceList({}, 'Error loading presence data');
        }
    }

    renderPresenceList(presence, errorMessage = null) {
        const tbody = document.getElementById('modal-presence-list');
        if (!tbody) return;

        if (errorMessage) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="px-4 py-8 text-center text-yellow-600 dark:text-yellow-400">
                        <span class="material-icons text-2xl mb-2">info</span>
                        <p>${errorMessage}</p>
                    </td>
                </tr>
            `;
            return;
        }

        const clients = Object.values(presence);

        if (clients.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                        No clients connected to this channel
                    </td>
                </tr>
            `;
            return;
        }

        let html = '';
        clients.forEach(client => {
            const userId = client.user || 'anonymous';
            const clientId = (client.client || '').substring(0, 12) + '...';
            const connInfo = client.conn_info ? JSON.stringify(client.conn_info) : '-';

            html += `
                <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">${this.escapeHtml(userId)}</td>
                    <td class="px-4 py-3 text-xs font-mono text-gray-600 dark:text-gray-400">${this.escapeHtml(clientId)}</td>
                    <td class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400">${this.escapeHtml(connInfo)}</td>
                </tr>
            `;
        });

        tbody.innerHTML = html;
    }

    async loadChannelHistory(channel) {
        try {
            const data = { channel, limit: 10 };
            const response = await this.api.centrifugoAdminApiServerHistoryCreate(data);

            if (response && response.error) {
                // Feature not available (e.g., code 108)
                console.warn('History not available:', response.error.message);
                this.renderHistoryList([], 'History not enabled for this channel');
                this.updateElement('modal-history-count', 'N/A');
            } else if (response && response.result) {
                const publications = response.result.publications || [];
                this.renderHistoryList(publications);
                this.updateElement('modal-history-count', publications.length);
            }
        } catch (error) {
            console.error('Error loading channel history:', error);
            this.renderHistoryList([], 'Error loading history');
            this.updateElement('modal-history-count', 'Error');
        }
    }

    renderHistoryList(publications, errorMessage = null) {
        const container = document.getElementById('modal-history-list');
        if (!container) return;

        if (errorMessage) {
            container.innerHTML = `
                <p class="text-sm text-yellow-600 dark:text-yellow-400 text-center py-4">
                    <span class="material-icons text-xl">info</span><br>
                    ${errorMessage}
                </p>
            `;
            return;
        }

        if (publications.length === 0) {
            container.innerHTML = `
                <p class="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                    No recent messages in this channel
                </p>
            `;
            return;
        }

        let html = '';
        publications.forEach((pub, index) => {
            const data = pub.data || {};
            const offset = pub.offset || '-';
            const dataStr = JSON.stringify(data, null, 2);

            html += `
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Message #${index + 1}</span>
                        <span class="text-xs text-gray-500 dark:text-gray-400">Offset: ${offset}</span>
                    </div>
                    <pre class="text-xs text-gray-900 dark:text-white overflow-x-auto"><code>${this.escapeHtml(dataStr)}</code></pre>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    closeModal() {
        const modal = document.getElementById('channel-details-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
        this.currentChannel = null;
    }

    updateLiveChannelsBadge(count) {
        const badge = document.getElementById('live-channels-count-badge');
        if (badge) {
            badge.textContent = count;
        }
    }

    showError(message) {
        const grid = document.getElementById('live-channels-grid');
        if (grid) {
            grid.innerHTML = `
                <div class="col-span-full bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <div class="flex items-center gap-3">
                        <span class="material-icons text-red-500">error</span>
                        <p class="text-sm text-red-700 dark:text-red-400">${this.escapeHtml(message)}</p>
                    </div>
                </div>
            `;
        }
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return unsafe;
        const div = document.createElement('div');
        div.textContent = unsafe;
        return div.innerHTML;
    }
}
