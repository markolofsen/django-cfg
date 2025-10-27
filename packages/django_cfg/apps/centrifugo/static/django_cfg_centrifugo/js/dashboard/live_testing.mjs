/**
 * Live Testing Module
 * Interactive WebSocket testing client for Centrifugo integration
 */

export class LiveTestingModule {
    constructor(api, dashboard) {
        this.api = api;
        this.dashboard = dashboard;
        this.centrifuge = null;
        this.subscriptions = new Map(); // channel -> subscription object
        this.receivedMessages = [];
        this.sentAcks = [];
        this.eventsLog = []; // WebSocket events log
        this.autoAck = true;
        this.clientId = this.generateClientId();
        this.connectionToken = null;
    }

    /**
     * Generate unique client ID for this session
     */
    generateClientId() {
        const stored = localStorage.getItem('centrifugo_client_id');
        if (stored) return stored;

        const id = 'client_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('centrifugo_client_id', id);
        return id;
    }

    /**
     * Log WebSocket event
     * @param {string} type - Event type: connection, subscription, publication, error, ack
     * @param {string} message - Human-readable message
     * @param {object} data - Additional event data
     */
    logEvent(type, message, data = null) {
        const event = {
            type,
            message,
            data,
            timestamp: new Date().toISOString()
        };

        this.eventsLog.unshift(event);

        // Limit to 100 events
        if (this.eventsLog.length > 100) {
            this.eventsLog = this.eventsLog.slice(0, 100);
        }

        console.log(`[${type.toUpperCase()}]`, message, data || '');
        this.renderEventsLog();
    }

    /**
     * Connect to Centrifugo WebSocket
     */
    async connectToCentrifugo(userId) {
        try {
            console.log('Requesting connection token...');
            this.logEvent('connection', 'Requesting connection token...', { user_id: userId });

            // Get JWT token from backend
            const tokenResponse = await this.api.centrifugoAdminApiTestingConnectionTokenCreate({
                user_id: userId || 'test-user',
                channels: []
            });

            if (!tokenResponse || !tokenResponse.token) {
                throw new Error('Failed to get connection token');
            }

            this.connectionToken = tokenResponse.token;
            const wsUrl = tokenResponse.centrifugo_url;

            console.log('Connecting to Centrifugo:', wsUrl);
            this.logEvent('connection', 'Connecting to Centrifugo...', { url: wsUrl });

            // Initialize Centrifuge client
            this.centrifuge = new Centrifuge(wsUrl, {
                token: this.connectionToken,
                debug: true
            });

            // Setup event handlers
            this.centrifuge.on('connected', (ctx) => {
                console.log('Connected to Centrifugo!', ctx);
                this.onConnected(ctx);
            });

            this.centrifuge.on('disconnected', (ctx) => {
                console.log('Disconnected from Centrifugo', ctx);
                this.onDisconnected(ctx);
            });

            this.centrifuge.on('error', (ctx) => {
                console.error('Centrifugo error:', ctx);
                this.onError(ctx);
            });

            // Connect
            this.centrifuge.connect();

            return { success: true };

        } catch (error) {
            console.error('Failed to connect to Centrifugo:', error);
            this.logEvent('error', 'Connection failed: ' + error.message, { error: error.message });
            return { success: false, error: error.message };
        }
    }

    /**
     * Disconnect from Centrifugo
     */
    disconnect() {
        if (this.centrifuge) {
            this.centrifuge.disconnect();
            this.centrifuge = null;
        }
        this.subscriptions.clear();
        this.updateConnectionStatus(false);
    }

    /**
     * Subscribe to channel
     */
    subscribeToChannel(channel) {
        if (!this.centrifuge) {
            alert('Connect to Centrifugo first!');
            return;
        }

        if (this.subscriptions.has(channel)) {
            alert(`Already subscribed to ${channel}`);
            return;
        }

        console.log('Subscribing to channel:', channel);

        const subscription = this.centrifuge.newSubscription(channel);

        // Handle publications
        subscription.on('publication', async (ctx) => {
            console.log('Received publication:', ctx.data);
            await this.onPublication(channel, ctx.data);
        });

        subscription.on('subscribed', (ctx) => {
            console.log(`Subscribed to ${channel}`, ctx);
            this.onSubscribed(channel);
        });

        subscription.on('unsubscribed', (ctx) => {
            console.log(`Unsubscribed from ${channel}`, ctx);
            this.onUnsubscribed(channel);
        });

        subscription.subscribe();
        this.subscriptions.set(channel, subscription);
    }

    /**
     * Unsubscribe from channel
     */
    unsubscribeFromChannel(channel) {
        const subscription = this.subscriptions.get(channel);
        if (subscription) {
            subscription.unsubscribe();
            this.subscriptions.delete(channel);
        }
    }

    /**
     * Publish test message via wrapper
     */
    async publishTestMessage(channel, data, waitForAck = false, ackTimeout = 10) {
        try {
            console.log('Publishing test message...', { channel, data, waitForAck });

            const response = await this.api.centrifugoAdminApiTestingPublishTestCreate({
                channel,
                data,
                wait_for_ack: waitForAck,
                ack_timeout: ackTimeout
            });

            console.log('Publish response:', response);

            return response;

        } catch (error) {
            console.error('Failed to publish test message:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Send manual ACK for message
     */
    async sendManualAck(messageId) {
        try {
            console.log('Sending manual ACK for message:', messageId);
            this.logEvent('ack', `Sending ACK for message ${messageId}`, { message_id: messageId });

            const response = await this.api.centrifugoAdminApiTestingSendAckCreate({
                message_id: messageId,
                client_id: this.clientId
            });

            console.log('ACK response:', response);

            if (response.success) {
                this.logEvent('ack', `ACK sent successfully for ${messageId}`, { message_id: messageId });
            } else {
                this.logEvent('error', `ACK failed for ${messageId}`, { message_id: messageId, error: response.error });
            }

            // Track sent ACK
            this.sentAcks.push({
                message_id: messageId,
                timestamp: new Date().toISOString(),
                success: response.success
            });

            this.renderAckHistory();

            return response;

        } catch (error) {
            console.error('Failed to send ACK:', error);
            this.logEvent('error', `ACK request failed: ${error.message}`, { message_id: messageId, error: error.message });
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Handle connection established
     */
    onConnected(ctx) {
        this.logEvent('connection', 'Connected to Centrifugo', { client_id: ctx.client });
        this.updateConnectionStatus(true);
        this.updateElement('ws-client-id', ctx.client);

        // Show success notification
        if (window.showNotification) {
            window.showNotification('Connected to Centrifugo!', 'success');
        }
    }

    /**
     * Handle disconnection
     */
    onDisconnected(ctx) {
        this.logEvent('connection', 'Disconnected from Centrifugo', { reason: ctx.reason, code: ctx.code });
        this.updateConnectionStatus(false);

        if (window.showNotification) {
            window.showNotification('Disconnected from Centrifugo', 'warning');
        }
    }

    /**
     * Handle connection error
     */
    onError(ctx) {
        console.error('Connection error:', ctx);
        this.logEvent('error', 'WebSocket error: ' + ctx.message, { error: ctx });

        if (window.showNotification) {
            window.showNotification('Centrifugo connection error: ' + ctx.message, 'error');
        }
    }

    /**
     * Handle incoming publication
     */
    async onPublication(channel, data) {
        this.logEvent('publication', `Message received on ${channel}`, {
            channel,
            message_id: data._message_id,
            ack_required: data._ack_required
        });

        // Add to received messages
        this.receivedMessages.unshift({
            channel,
            data,
            timestamp: new Date().toISOString(),
            ack_required: data._ack_required || false,
            message_id: data._message_id || null,
            ack_sent: false
        });

        // Limit history to 50 messages
        if (this.receivedMessages.length > 50) {
            this.receivedMessages = this.receivedMessages.slice(0, 50);
        }

        // Render message in UI
        this.renderReceivedMessages();

        // Auto-send ACK if required and enabled
        if (this.autoAck && data._ack_required && data._message_id) {
            console.log('Auto-sending ACK for message:', data._message_id);
            await this.sendManualAck(data._message_id);

            // Mark message as ACK sent
            const msg = this.receivedMessages.find(m => m.message_id === data._message_id);
            if (msg) {
                msg.ack_sent = true;
                this.renderReceivedMessages();
            }
        }
    }

    /**
     * Handle channel subscription success
     */
    onSubscribed(channel) {
        this.logEvent('subscription', `Subscribed to ${channel}`, { channel });
        this.renderSubscriptionsList();

        if (window.showNotification) {
            window.showNotification(`Subscribed to ${channel}`, 'success');
        }
    }

    /**
     * Handle channel unsubscription
     */
    onUnsubscribed(channel) {
        this.logEvent('subscription', `Unsubscribed from ${channel}`, { channel });
        this.renderSubscriptionsList();

        if (window.showNotification) {
            window.showNotification(`Unsubscribed from ${channel}`, 'info');
        }
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('ws-connection-status');
        const connectBtn = document.getElementById('ws-connect-btn');
        const disconnectBtn = document.getElementById('ws-disconnect-btn');
        const subscribeBtn = document.getElementById('ws-subscribe-btn');

        if (statusEl) {
            if (connected) {
                statusEl.textContent = 'Connected';
                statusEl.className = 'px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-sm font-medium';
            } else {
                statusEl.textContent = 'Disconnected';
                statusEl.className = 'px-3 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-full text-sm font-medium';
            }
        }

        if (connectBtn) connectBtn.disabled = connected;
        if (disconnectBtn) disconnectBtn.disabled = !connected;
        if (subscribeBtn) subscribeBtn.disabled = !connected;
    }

    /**
     * Render subscriptions list
     */
    renderSubscriptionsList() {
        const container = document.getElementById('ws-subscriptions-list');
        if (!container) return;

        if (this.subscriptions.size === 0) {
            container.innerHTML = `
                <div class="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
                    No active subscriptions
                </div>
            `;
            return;
        }

        let html = '<div class="space-y-2">';
        this.subscriptions.forEach((sub, channel) => {
            html += `
                <div class="flex items-center justify-between bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                    <div class="flex items-center gap-2">
                        <span class="material-icons text-purple-500 text-sm">radio_button_checked</span>
                        <code class="text-sm font-mono text-gray-900 dark:text-white">${this.escapeHtml(channel)}</code>
                    </div>
                    <button onclick="window.centrifugoDashboard.liveTestingModule.unsubscribeFromChannel('${this.escapeHtml(channel)}')"
                            class="px-3 py-1 bg-red-500 hover:bg-red-600 text-white rounded text-xs font-medium">
                        Unsubscribe
                    </button>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;

        // Update count badge
        const badge = document.getElementById('ws-subscriptions-count');
        if (badge) {
            badge.textContent = this.subscriptions.size;
        }
    }

    /**
     * Render received messages
     */
    renderReceivedMessages() {
        const container = document.getElementById('ws-received-messages');
        if (!container) return;

        if (this.receivedMessages.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                    No messages received yet...
                </div>
            `;
            return;
        }

        let html = '<div class="space-y-3">';
        this.receivedMessages.forEach(msg => {
            const timeStr = new Date(msg.timestamp).toLocaleTimeString();
            const ackBadge = msg.ack_required ?
                (msg.ack_sent ?
                    '<span class="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">ACK Sent</span>' :
                    '<span class="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded text-xs">ACK Required</span>'
                ) : '';

            html += `
                <div class="bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                    <div class="flex items-start justify-between mb-2">
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-1">
                                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">${timeStr}</span>
                                <code class="text-xs bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 px-2 py-0.5 rounded">${this.escapeHtml(msg.channel)}</code>
                                ${ackBadge}
                            </div>
                        </div>
                        ${msg.ack_required && !msg.ack_sent && msg.message_id ? `
                            <button onclick="window.centrifugoDashboard.liveTestingModule.sendManualAck('${msg.message_id}')"
                                    class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs font-medium flex items-center gap-1">
                                <span class="material-icons text-sm">check</span>
                                Send ACK
                            </button>
                        ` : ''}
                    </div>
                    <pre class="text-xs bg-gray-50 dark:bg-gray-800 p-3 rounded overflow-x-auto"><code>${this.escapeHtml(JSON.stringify(msg.data, null, 2))}</code></pre>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;

        // Update count
        const countEl = document.getElementById('ws-messages-count');
        if (countEl) {
            countEl.textContent = this.receivedMessages.length;
        }
    }

    /**
     * Render ACK history
     */
    renderAckHistory() {
        const container = document.getElementById('ws-ack-history');
        if (!container) return;

        if (this.sentAcks.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
                    No ACKs sent yet
                </div>
            `;
            return;
        }

        let html = '<div class="space-y-2">';
        this.sentAcks.slice().reverse().slice(0, 10).forEach(ack => {
            const timeStr = new Date(ack.timestamp).toLocaleTimeString();
            const statusIcon = ack.success ?
                '<span class="material-icons text-green-500 text-sm">check_circle</span>' :
                '<span class="material-icons text-red-500 text-sm">error</span>';

            html += `
                <div class="flex items-center justify-between bg-gray-50 dark:bg-gray-700 rounded p-2">
                    <div class="flex items-center gap-2">
                        ${statusIcon}
                        <code class="text-xs font-mono text-gray-900 dark:text-white">${this.escapeHtml(ack.message_id.substring(0, 12))}...</code>
                    </div>
                    <span class="text-xs text-gray-500 dark:text-gray-400">${timeStr}</span>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;
    }

    /**
     * Render events log
     */
    renderEventsLog() {
        const container = document.getElementById('ws-events-log');
        if (!container) return;

        if (this.eventsLog.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
                    No events logged yet
                </div>
            `;
            return;
        }

        let html = '<div class="space-y-1 max-h-[400px] overflow-y-auto">';
        this.eventsLog.forEach(event => {
            const timeStr = new Date(event.timestamp).toLocaleTimeString();

            // Color coding by event type
            let colorClass = 'text-gray-600 dark:text-gray-400';
            let iconName = 'info';
            let bgClass = 'bg-gray-50 dark:bg-gray-700';

            switch (event.type) {
                case 'connection':
                    colorClass = 'text-green-600 dark:text-green-400';
                    iconName = 'link';
                    bgClass = 'bg-green-50 dark:bg-green-900/20';
                    break;
                case 'subscription':
                    colorClass = 'text-blue-600 dark:text-blue-400';
                    iconName = 'radio_button_checked';
                    bgClass = 'bg-blue-50 dark:bg-blue-900/20';
                    break;
                case 'publication':
                    colorClass = 'text-purple-600 dark:text-purple-400';
                    iconName = 'message';
                    bgClass = 'bg-purple-50 dark:bg-purple-900/20';
                    break;
                case 'ack':
                    colorClass = 'text-indigo-600 dark:text-indigo-400';
                    iconName = 'check_circle';
                    bgClass = 'bg-indigo-50 dark:bg-indigo-900/20';
                    break;
                case 'error':
                    colorClass = 'text-red-600 dark:text-red-400';
                    iconName = 'error';
                    bgClass = 'bg-red-50 dark:bg-red-900/20';
                    break;
            }

            html += `
                <div class="${bgClass} rounded p-2 hover:shadow-sm transition-shadow">
                    <div class="flex items-start gap-2">
                        <span class="material-icons text-sm ${colorClass} flex-shrink-0 mt-0.5">${iconName}</span>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-2 mb-0.5">
                                <span class="text-xs font-medium ${colorClass} uppercase">${event.type}</span>
                                <span class="text-xs text-gray-500 dark:text-gray-400">${timeStr}</span>
                            </div>
                            <p class="text-xs text-gray-700 dark:text-gray-300">${this.escapeHtml(event.message)}</p>
                            ${event.data ? `
                                <details class="mt-1">
                                    <summary class="text-xs text-gray-500 dark:text-gray-400 cursor-pointer hover:text-gray-700 dark:hover:text-gray-200">
                                        Details
                                    </summary>
                                    <pre class="text-xs bg-white dark:bg-gray-800 p-2 rounded mt-1 overflow-x-auto"><code>${this.escapeHtml(JSON.stringify(event.data, null, 2))}</code></pre>
                                </details>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;

        // Update count badge
        const badge = document.getElementById('ws-events-count');
        if (badge) {
            badge.textContent = this.eventsLog.length;
        }
    }

    /**
     * Clear events log
     */
    clearEventsLog() {
        this.eventsLog = [];
        this.renderEventsLog();
        this.logEvent('connection', 'Events log cleared');
    }

    /**
     * Export events log to JSON
     */
    exportEventsLog() {
        const dataStr = JSON.stringify(this.eventsLog, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `centrifugo-events-${new Date().toISOString()}.json`;
        link.click();
        URL.revokeObjectURL(url);

        this.logEvent('connection', 'Events log exported to JSON');
    }

    /**
     * Clear received messages
     */
    clearReceivedMessages() {
        this.receivedMessages = [];
        this.renderReceivedMessages();
    }

    /**
     * Clear ACK history
     */
    clearAckHistory() {
        this.sentAcks = [];
        this.renderAckHistory();
    }

    /**
     * Toggle auto ACK
     */
    toggleAutoAck(enabled) {
        this.autoAck = enabled;
        console.log('Auto ACK:', this.autoAck ? 'enabled' : 'disabled');
    }

    /**
     * Run quick test scenario
     */
    async runQuickScenario(scenarioName) {
        console.log('Running quick scenario:', scenarioName);

        const scenarios = {
            'simple-notification': {
                name: 'Simple Notification',
                channel: 'user#test-123',
                data: {
                    type: 'notification',
                    title: 'Test Notification',
                    message: 'This is a simple test notification',
                    timestamp: new Date().toISOString()
                },
                waitForAck: false,
                autoConnect: true,
                autoSubscribe: true
            },
            'ack-notification': {
                name: 'ACK Required Notification',
                channel: 'user#test-123',
                data: {
                    type: 'important',
                    title: 'Important Message',
                    message: 'Please acknowledge this message',
                    priority: 'high',
                    timestamp: new Date().toISOString()
                },
                waitForAck: true,
                ackTimeout: 10,
                autoConnect: true,
                autoSubscribe: true
            },
            'broadcast': {
                name: 'Team Broadcast',
                channel: 'team#developers',
                data: {
                    type: 'broadcast',
                    title: 'Team Announcement',
                    message: 'Testing broadcast to all team members',
                    from: 'admin',
                    timestamp: new Date().toISOString()
                },
                waitForAck: false,
                autoConnect: true,
                autoSubscribe: true
            },
            'ack-flow': {
                name: 'Complete ACK Flow Test',
                channel: 'test#ack-flow',
                data: {
                    type: 'test',
                    title: 'ACK Flow Test',
                    message: 'Testing complete publish → receive → ACK flow',
                    test_id: Math.random().toString(36).substr(2, 9),
                    timestamp: new Date().toISOString()
                },
                waitForAck: true,
                ackTimeout: 15,
                autoConnect: true,
                autoSubscribe: true
            }
        };

        const scenario = scenarios[scenarioName];
        if (!scenario) {
            alert('Unknown scenario: ' + scenarioName);
            return;
        }

        try {
            // Step 1: Connect if needed
            if (scenario.autoConnect && !this.centrifuge) {
                if (window.showNotification) {
                    window.showNotification('Connecting to Centrifugo...', 'info');
                }
                const connectResult = await this.connectToCentrifugo('test-user-123');
                if (!connectResult.success) {
                    throw new Error('Failed to connect: ' + connectResult.error);
                }
                // Wait for connection
                await new Promise(resolve => setTimeout(resolve, 1000));
            }

            // Step 2: Subscribe if needed
            if (scenario.autoSubscribe && !this.subscriptions.has(scenario.channel)) {
                if (window.showNotification) {
                    window.showNotification('Subscribing to ' + scenario.channel + '...', 'info');
                }
                this.subscribeToChannel(scenario.channel);
                // Wait for subscription
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            // Step 3: Publish message
            if (window.showNotification) {
                window.showNotification('Publishing test message...', 'info');
            }

            const result = await this.publishTestMessage(
                scenario.channel,
                scenario.data,
                scenario.waitForAck || false,
                scenario.ackTimeout || 10
            );

            // Step 4: Show result
            if (result.success) {
                let message = `✅ Scenario "${scenario.name}" completed!\n\n`;
                message += `Message ID: ${result.message_id}\n`;
                message += `Channel: ${result.channel}\n`;
                if (scenario.waitForAck) {
                    message += `ACKs Received: ${result.acks_received}\n`;
                    message += `Delivered: ${result.delivered ? 'Yes' : 'No'}`;
                }

                alert(message);

                if (window.showNotification) {
                    window.showNotification('Scenario completed successfully!', 'success');
                }
            } else {
                throw new Error(result.error || 'Unknown error');
            }

        } catch (error) {
            console.error('Scenario failed:', error);
            alert('❌ Scenario failed: ' + error.message);

            if (window.showNotification) {
                window.showNotification('Scenario failed: ' + error.message, 'error');
            }
        }
    }

    /**
     * Update element text content
     */
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Escape HTML for safe rendering
     */
    escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return unsafe;
        const div = document.createElement('div');
        div.textContent = unsafe;
        return div.innerHTML;
    }
}
