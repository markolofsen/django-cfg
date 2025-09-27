/**
 * Ngrok Status Component
 * 
 * Alpine.js component for displaying and managing ngrok tunnel status.
 */

// Ensure PaymentSystem namespace exists
window.PaymentSystem = window.PaymentSystem || {};
window.PaymentSystem.Components = window.PaymentSystem.Components || {};

/**
 * Ngrok Status Card Component
 */
window.PaymentSystem.Components.ngrokStatus = function() {
    return {
        status: {
            active: false,
            public_url: '',
            webhook_url: '',
            region: 'us',
            proto: 'https',
            error: null
        },
        refreshing: false,

        async init() {
            await this.loadStatus();
            // Auto-refresh every 30 seconds
            setInterval(() => this.loadStatus(), 30000);
        },

        async loadStatus() {
            try {
                // Use our health check endpoint instead of direct ngrok API
                const response = await fetch('/api/payments/webhooks/health/');
                if (response.ok) {
                    const data = await response.json();
                    const ngrokActive = data.details?.ngrok_available || false;
                    const apiUrl = data.details?.api_base_url || '';
                    
                    if (ngrokActive) {
                        this.status = {
                            active: true,
                            public_url: apiUrl,
                            webhook_url: apiUrl + '/api/payments/webhooks/',
                            region: 'auto',
                            proto: apiUrl.startsWith('https') ? 'https' : 'http',
                            error: null
                        };
                    } else {
                        this.status = {
                            active: false,
                            public_url: '',
                            webhook_url: '',
                            region: 'us',
                            proto: 'https',
                            error: 'Ngrok tunnel not active'
                        };
                    }
                } else {
                    this.status = {
                        active: false,
                        public_url: '',
                        webhook_url: '',
                        region: 'us',
                        proto: 'https',
                        error: 'Health check API not accessible'
                    };
                }
            } catch (error) {
                console.error('Failed to fetch Ngrok status:', error);
                this.status = {
                    active: false,
                    public_url: '',
                    webhook_url: '',
                    region: 'us',
                    proto: 'https',
                    error: error.message || 'Failed to check ngrok status'
                };
            }
        },

        async refreshStatus() {
            this.refreshing = true;
            try {
                await this.loadStatus();
            } finally {
                this.refreshing = false;
            }
        },

        async copyUrl() {
            if (this.status.public_url) {
                try {
                    await navigator.clipboard.writeText(this.status.public_url);
                    this.$dispatch('show-notification', {
                        type: 'success',
                        message: 'Public URL copied to clipboard'
                    });
                } catch (error) {
                    console.error('Failed to copy URL:', error);
                    this.$dispatch('show-notification', {
                        type: 'error',
                        message: 'Failed to copy URL to clipboard'
                    });
                }
            }
        },

        async copyWebhookUrl() {
            if (this.status.webhook_url) {
                try {
                    await navigator.clipboard.writeText(this.status.webhook_url);
                    this.$dispatch('show-notification', {
                        type: 'success',
                        message: 'Webhook URL copied to clipboard'
                    });
                } catch (error) {
                    console.error('Failed to copy webhook URL:', error);
                    this.$dispatch('show-notification', {
                        type: 'error',
                        message: 'Failed to copy webhook URL to clipboard'
                    });
                }
            }
        },

        openInBrowser() {
            if (this.status.public_url) {
                window.open(this.status.public_url, '_blank');
            }
        },

        async startTunnel() {
            // This would typically call a backend endpoint to start ngrok
            this.$dispatch('show-notification', {
                type: 'info',
                message: 'Starting ngrok tunnel... (This feature requires backend implementation)'
            });
        },

        async stopTunnel() {
            // This would typically call a backend endpoint to stop ngrok
            this.$dispatch('show-notification', {
                type: 'info',
                message: 'Stopping ngrok tunnel... (This feature requires backend implementation)'
            });
        }
    };
};

// Global function for backward compatibility
window.ngrokStatus = window.PaymentSystem.Components.ngrokStatus;

// Also define it directly for immediate availability
if (!window.ngrokStatus) {
    window.ngrokStatus = window.PaymentSystem.Components.ngrokStatus;
}

// Debug: Log that the component is loaded
console.log('Ngrok Status component loaded:', typeof window.ngrokStatus);
console.log('PaymentSystem namespace:', window.PaymentSystem);
console.log('Available functions:', Object.keys(window).filter(key => key.includes('ngrok')));
