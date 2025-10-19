/**
 * Payment Details Dialog (v2.0 - Simplified)
 * Shows payment details with QR code, address, and status
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  Button,
  TokenIcon,
} from '@djangocfg/ui';
import { Copy, ExternalLink, CheckCircle2, Clock, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { Hooks, api } from '@djangocfg/api';
import type { API } from '@djangocfg/api';
import { PAYMENT_EVENTS } from '../events';

export const PaymentDetailsDialog: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [paymentId, setPaymentId] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [timeLeft, setTimeLeft] = useState<string>('');

  // Load payment data by ID using hook
  const shouldFetch = open && !!paymentId;
  const { data: payment, isLoading, error, mutate } = Hooks.usePaymentsPaymentsRetrieve(
    shouldFetch ? paymentId : '',
    api as unknown as API
  );

  // Listen for open/close events
  useEffect(() => {
    const handleOpen = (event: Event) => {
      const customEvent = event as CustomEvent<{ id: string }>;
      setPaymentId(customEvent.detail.id);
      setOpen(true);
    };

    const handleClose = () => {
      setOpen(false);
      setPaymentId(null);
    };

    window.addEventListener(PAYMENT_EVENTS.OPEN_PAYMENT_DETAILS_DIALOG, handleOpen);
    window.addEventListener(PAYMENT_EVENTS.CLOSE_DIALOG, handleClose);

    return () => {
      window.removeEventListener(PAYMENT_EVENTS.OPEN_PAYMENT_DETAILS_DIALOG, handleOpen);
      window.removeEventListener(PAYMENT_EVENTS.CLOSE_DIALOG, handleClose);
    };
  }, []);

  const handleClose = () => {
    setOpen(false);
    setPaymentId(null);
  };

  const handleCopyAddress = async () => {
    if (payment?.pay_address) {
      await navigator.clipboard.writeText(payment.pay_address);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Calculate time left until expiration
  useEffect(() => {
    if (!payment?.expires_at) return;

    const updateTimeLeft = () => {
      const now = new Date().getTime();
      const expires = new Date(payment.expires_at!).getTime();
      const diff = expires - now;

      if (diff <= 0) {
        setTimeLeft('Expired');
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      setTimeLeft(`${hours}h ${minutes}m ${seconds}s`);
    };

    updateTimeLeft();
    const interval = setInterval(updateTimeLeft, 1000);

    return () => clearInterval(interval);
  }, [payment?.expires_at]);

  // Get status icon and color
  const getStatusInfo = () => {
    switch (payment?.status?.toLowerCase()) {
      case 'pending':
        return { icon: Clock, color: 'text-yellow-500', bg: 'bg-yellow-500/10' };
      case 'completed':
      case 'success':
        return { icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-500/10' };
      case 'failed':
      case 'error':
        return { icon: XCircle, color: 'text-red-500', bg: 'bg-red-500/10' };
      case 'expired':
        return { icon: AlertCircle, color: 'text-gray-500', bg: 'bg-gray-500/10' };
      case 'confirming':
        return { icon: RefreshCw, color: 'text-blue-500', bg: 'bg-blue-500/10' };
      default:
        return { icon: Clock, color: 'text-gray-500', bg: 'bg-gray-500/10' };
    }
  };

  if (!open) return null;

  // Loading state
  if (isLoading) {
    return (
      <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Payment Details</DialogTitle>
            <DialogDescription>Loading payment information...</DialogDescription>
          </DialogHeader>
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // Error state
  if (shouldFetch && !isLoading && (error || !payment)) {
    return (
      <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Payment Details</DialogTitle>
            <DialogDescription>Failed to load payment information</DialogDescription>
          </DialogHeader>
          <div className="flex flex-col items-center justify-center py-12 space-y-4">
            <XCircle className="h-12 w-12 text-destructive" />
            <p className="text-sm text-muted-foreground">
              {error ? `Error: ${error}` : 'Payment not found'}
            </p>
            <Button onClick={() => mutate()}>Try Again</Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  const statusInfo = getStatusInfo();
  const StatusIcon = statusInfo.icon;

  // Generate QR code URL
  const qrCodeUrl = payment.pay_address
    ? `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(payment.pay_address)}`
    : null;

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Payment Details</DialogTitle>
          <DialogDescription>
            Send cryptocurrency to complete your payment
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status Badge */}
          <div className={`flex items-center gap-3 p-4 rounded-sm ${statusInfo.bg}`}>
            <StatusIcon className={`h-5 w-5 ${statusInfo.color}`} />
            <div className="flex-1">
              <div className="font-semibold capitalize">{payment.status}</div>
              {payment.status === 'pending' && timeLeft && (
                <div className="text-sm text-muted-foreground">
                  Expires in {timeLeft}
                </div>
              )}
            </div>
          </div>

          {/* Amount Information */}
          <div className="space-y-3">
            <div className="flex items-center justify-between p-4 bg-muted rounded-sm">
              <span className="text-sm text-muted-foreground">Amount to send</span>
              <div className="flex items-center gap-2">
                <TokenIcon symbol={String(payment.currency_code || 'BTC')} size={20} />
                <span className="font-mono font-bold text-lg">
                  {payment.pay_amount || '0.00000000'} {payment.currency_code}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between px-4">
              <span className="text-sm text-muted-foreground">Equivalent to</span>
              <span className="font-semibold text-lg">
                ${parseFloat(payment.amount_usd || '0').toFixed(2)} USD
              </span>
            </div>

            {payment.internal_payment_id && (
              <div className="flex items-center justify-between px-4">
                <span className="text-sm text-muted-foreground">Payment Order #</span>
                <span className="font-mono font-medium">{payment.internal_payment_id}</span>
              </div>
            )}

            {payment.currency_network && (
              <div className="flex items-center justify-between px-4">
                <span className="text-sm text-muted-foreground">Network</span>
                <span className="font-medium">{payment.currency_network}</span>
              </div>
            )}
          </div>

          {/* QR Code */}
          {qrCodeUrl && payment.status === 'pending' && (
            <div className="flex justify-center p-6 bg-white rounded-sm">
              <img src={qrCodeUrl} alt="Payment QR Code" className="w-48 h-48" />
            </div>
          )}

          {/* Payment Address */}
          {payment.pay_address && payment.status === 'pending' && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Payment Address</label>
              <div className="flex items-center gap-2">
                <div className="flex-1 p-3 bg-muted rounded-sm font-mono text-sm break-all">
                  {payment.pay_address}
                </div>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleCopyAddress}
                  className="shrink-0"
                >
                  {copied ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          )}

          {/* Transaction Hash */}
          {payment.transaction_hash && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Transaction Hash</label>
              <div className="p-3 bg-muted rounded-sm font-mono text-sm break-all">
                {payment.transaction_hash}
              </div>
            </div>
          )}

          {/* Payment URL */}
          {payment.payment_url && payment.status === 'pending' && (
            <Button
              variant="outline"
              className="w-full"
              onClick={() => window.open(payment.payment_url!, '_blank')}
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Open in Payment Provider
            </Button>
          )}

          {/* Additional Info */}
          <div className="pt-4 border-t space-y-2 text-xs text-muted-foreground">
            <div className="flex justify-between">
              <span>Payment ID</span>
              <span className="font-mono">{payment.id}</span>
            </div>
            <div className="flex justify-between">
              <span>Created</span>
              <span>{new Date(payment.created_at!).toLocaleString()}</span>
            </div>
            {payment.confirmations_count !== undefined && (
              <div className="flex justify-between">
                <span>Confirmations</span>
                <span>{payment.confirmations_count}</span>
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Close
          </Button>
          <Button onClick={() => mutate()} variant="ghost" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
