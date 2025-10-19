/**
 * Recent Payments Component (v2.0 - Simplified)
 * Display recent payment transactions from payments list
 */

'use client';

import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Skeleton,
} from '@djangocfg/ui';
import { History, ExternalLink } from 'lucide-react';
import { useOverviewContext } from '@djangocfg/api/cfg/contexts';
import { openPaymentDetailsDialog } from '../../../events';

export const RecentPayments: React.FC = () => {
  const { payments, isLoadingPayments } = useOverviewContext();

  const formatCurrency = (amount?: number | string | null) => {
    if (amount === null || amount === undefined) return '$0.00';
    const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(numAmount);
  };

  const getRelativeTime = (date: string | null | undefined): string => {
    if (!date) return 'N/A';

    const now = new Date();
    const target = new Date(date);
    const diffInSeconds = Math.floor((now.getTime() - target.getTime()) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  const getStatusVariant = (
    status: string | null | undefined
  ): 'default' | 'destructive' | 'outline' | 'secondary' => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'success':
        return 'default';
      case 'pending':
      case 'confirming':
        return 'secondary';
      case 'failed':
      case 'error':
      case 'expired':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  if (isLoadingPayments) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Recent Payments
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between p-3 border rounded-sm">
              <div className="space-y-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-24" />
              </div>
              <Skeleton className="h-6 w-16" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  // Get first 5 payments for recent list
  const recentPaymentsList = payments?.results?.slice(0, 5) || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Recent Payments
          </div>
          <Button variant="ghost" size="sm">
            View All
            <ExternalLink className="h-4 w-4 ml-2" />
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {recentPaymentsList.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <History className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No recent payments</p>
            <p className="text-sm mt-2">Create your first payment to get started</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recentPaymentsList.map((payment) => (
              <div
                key={payment.id}
                className="flex items-center justify-between p-3 border rounded-sm hover:bg-accent cursor-pointer transition-colors"
                onClick={() => openPaymentDetailsDialog(String(payment.id))}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{formatCurrency(payment.amount_usd)}</span>
                    <Badge variant={getStatusVariant(payment.status)} className="text-xs">
                      {payment.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {getRelativeTime(payment.created_at)} • {payment.currency_code || 'USD'}
                  </p>
                </div>
                <ExternalLink className="h-4 w-4 text-muted-foreground" />
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
