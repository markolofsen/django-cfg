/**
 * Payment Detail Page JavaScript
 * Handles payment detail page functionality including AJAX status refresh
 */

function paymentDetail() {
    return {
        loading: false,
        showQRCode: false,
        paymentId: null,
        
        init(paymentId) {
            this.paymentId = paymentId;
            // Show QR code by default if payment address exists
            const payAddress = document.querySelector('[data-field="pay_address"]');
            if (payAddress && payAddress.textContent.trim()) {
                this.showQRCode = true;
            }
        },
        
        async refreshPaymentStatus() {
            this.loading = true;
            try {
                // Use the existing PaymentAPI client
                const data = await PaymentAPI.admin.payments.refreshStatus(this.paymentId);
                
                if (data.success) {
                    // Show success notification
                    PaymentAPI.utils.showNotification(data.message, 'success');
                    
                    // Update payment data on page without full reload
                    this.updatePaymentData(data.payment);
                } else {
                    // Show error notification
                    PaymentAPI.utils.showNotification(data.message || 'Failed to refresh payment status', 'error');
                }
            } catch (error) {
                console.error('Failed to refresh payment status:', error);
                PaymentAPI.utils.showNotification('Network error while refreshing status', 'error');
            } finally {
                this.loading = false;
            }
        },
        
        updatePaymentData(paymentData) {
            // Update status badge
            const statusBadge = document.querySelector('.payment-status-badge');
            if (statusBadge && paymentData.status) {
                statusBadge.textContent = paymentData.status.toUpperCase();
                statusBadge.className = `payment-status-badge inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${this.getStatusBadgeClass(paymentData.status)}`;
            }
            
            // Update other fields that might have changed
            const fields = {
                'pay_amount': paymentData.pay_amount,
                'transaction_hash': paymentData.transaction_hash,
                'pay_address': paymentData.pay_address,
                'payment_url': paymentData.payment_url,
                'expires_at': paymentData.expires_at,
                'confirmed_at': paymentData.confirmed_at,
                'updated_at': paymentData.updated_at,
                'status_changed_at': paymentData.status_changed_at
            };
            
            Object.entries(fields).forEach(([field, value]) => {
                const element = document.querySelector(`[data-field="${field}"]`);
                if (element && value !== null && value !== undefined) {
                    if (field.includes('_at') && value) {
                        // Format datetime fields
                        element.textContent = new Date(value).toLocaleString();
                    } else if (field === 'pay_amount' && paymentData.currency) {
                        // Format pay_amount with currency
                        element.textContent = `${parseFloat(value).toFixed(8)} ${paymentData.currency.code}`;
                    } else {
                        element.textContent = value;
                    }
                }
            });
            
            // Update error info if present
            if (paymentData.error_info) {
                const errorElement = document.querySelector('[data-field="error_info"]');
                if (errorElement) {
                    errorElement.textContent = JSON.stringify(paymentData.error_info, null, 2);
                }
            }
            
            // Update QR code visibility if pay_address changed
            if (paymentData.pay_address && !this.showQRCode) {
                this.showQRCode = true;
            }
        },
        
        getStatusBadgeClass(status) {
            const statusClasses = {
                'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
                'confirming': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
                'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
                'confirmed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
                'failed': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
                'cancelled': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
                'expired': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
                'refunded': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300'
            };
            return statusClasses[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
        },
        
        async cancelPayment() {
            if (!confirm('Are you sure you want to cancel this payment?')) {
                return;
            }
            
            this.loading = true;
            try {
                const data = await PaymentAPI.admin.payments.cancel(this.paymentId);
                PaymentAPI.utils.showNotification('Payment cancelled successfully', 'success');
                
                // Update payment data
                this.updatePaymentData(data);
            } catch (error) {
                console.error('Failed to cancel payment:', error);
                PaymentAPI.utils.showNotification('Failed to cancel payment', 'error');
            } finally {
                this.loading = false;
            }
        },
        
        exportDetails() {
            // Get payment data from the page
            const paymentData = {
                id: this.paymentId,
                status: document.querySelector('.payment-status-badge')?.textContent || 'Unknown',
                amount_usd: document.querySelector('[data-field="amount_usd"]')?.textContent || '',
                pay_amount: document.querySelector('[data-field="pay_amount"]')?.textContent || '',
                currency: document.querySelector('[data-field="currency"]')?.textContent || '',
                provider: document.querySelector('[data-field="provider"]')?.textContent || '',
                pay_address: document.querySelector('[data-field="pay_address"]')?.textContent || '',
                transaction_hash: document.querySelector('[data-field="transaction_hash"]')?.textContent || '',
                created_at: document.querySelector('[data-field="created_at"]')?.textContent || '',
                updated_at: document.querySelector('[data-field="updated_at"]')?.textContent || ''
            };
            
            // Create CSV content
            const csvContent = Object.entries(paymentData)
                .map(([key, value]) => `${key},${value}`)
                .join('\n');
            
            // Download CSV
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `payment_${this.paymentId}_details.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
    };
}

// Auto-initialize if PaymentAPI is available
document.addEventListener('DOMContentLoaded', function() {
    if (typeof PaymentAPI === 'undefined') {
        console.warn('PaymentAPI not found. Make sure api-client.js is loaded before payment-detail.js');
    }
});
