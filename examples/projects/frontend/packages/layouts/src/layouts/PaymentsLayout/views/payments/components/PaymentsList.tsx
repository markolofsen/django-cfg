/**
 * Payments List Component (v2.0 - Simplified)
 * Display paginated list of payments with filters
 */

'use client';

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Button,
  Badge,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Skeleton,
} from '@djangocfg/ui';
import { Plus, Search, Filter, ChevronLeft, ChevronRight, RefreshCw, ExternalLink } from 'lucide-react';
import { usePaymentsContext } from '@djangocfg/api/cfg/contexts';
import { openCreatePaymentDialog, openPaymentDetailsDialog } from '../../../events';

export const PaymentsList: React.FC = () => {
  const {
    payments,
    isLoadingPayments,
    refreshPayments,
  } = usePaymentsContext();

  const paymentsList = payments?.results || [];
  const currentPage = payments?.page || 1;
  const pageSize = payments?.page_size || 20;
  const totalCount = payments?.count || 0;

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

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

  const handleSearch = async (value: string) => {
    setSearchTerm(value);
    // TODO: Implement search/filter in PaymentsContext when API supports it
    await refreshPayments();
  };

  const handleStatusFilter = async (status: string) => {
    setStatusFilter(status);
    // TODO: Implement status filter in PaymentsContext when API supports it
    await refreshPayments();
  };

  const handlePageChange = async (page: number) => {
    // TODO: Implement pagination in PaymentsContext
    await refreshPayments();
  };

  // Filter payments client-side for now (until API supports filtering)
  const filteredPayments = paymentsList.filter((payment) => {
    const matchesSearch = searchTerm
      ? payment.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        payment.status?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        payment.currency_code?.toLowerCase().includes(searchTerm.toLowerCase())
      : true;

    const matchesStatus = statusFilter !== 'all'
      ? payment.status?.toLowerCase() === statusFilter.toLowerCase()
      : true;

    return matchesSearch && matchesStatus;
  });

  const totalPages = Math.ceil((totalCount || 0) / (pageSize || 20));
  const showingFrom = ((currentPage || 1) - 1) * (pageSize || 20) + 1;
  const showingTo = Math.min((currentPage || 1) * (pageSize || 20), totalCount || 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Payment History</span>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={refreshPayments} disabled={isLoadingPayments}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoadingPayments ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button size="sm" onClick={() => openCreatePaymentDialog()}>
              <Plus className="h-4 w-4 mr-2" />
              New Payment
            </Button>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by ID, status, or currency..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select value={statusFilter} onValueChange={handleStatusFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="confirming">Confirming</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
              <SelectItem value="expired">Expired</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Payments Table */}
        {isLoadingPayments ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center justify-between p-4 border rounded-sm">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-24" />
                </div>
                <Skeleton className="h-6 w-16" />
              </div>
            ))}
          </div>
        ) : filteredPayments.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 bg-muted rounded-full flex items-center justify-center">
              <Search className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No Payments Found</h3>
            <p className="text-muted-foreground mb-4">
              {searchTerm || statusFilter !== 'all'
                ? 'No payments match your current filters'
                : "You haven't made any payments yet"}
            </p>
            <Button onClick={() => openCreatePaymentDialog()}>
              <Plus className="h-4 w-4 mr-2" />
              Create Payment
            </Button>
          </div>
        ) : (
          <>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Currency</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Provider</TableHead>
                    <TableHead>Payment ID</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPayments.map((payment) => (
                    <TableRow
                      key={payment.id}
                      className="cursor-pointer hover:bg-accent"
                      onClick={() => openPaymentDetailsDialog(String(payment.id))}
                    >
                      <TableCell>
                        <div>
                          <div className="font-medium">
                            {payment.created_at
                              ? new Date(payment.created_at).toLocaleDateString()
                              : 'N/A'}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {getRelativeTime(payment.created_at)}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono font-semibold">
                        {formatCurrency(payment.amount_usd)}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{payment.currency_code || 'USD'}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusVariant(payment.status)}>{payment.status}</Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        NowPayments
                      </TableCell>
                      <TableCell className="font-mono text-sm text-muted-foreground">
                        {payment.id ? `${payment.id.toString().slice(0, 8)}...` : 'N/A'}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            openPaymentDetailsDialog(String(payment.id));
                          }}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  Showing {showingFrom} to {showingTo} of {totalCount} payments
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange((currentPage || 1) - 1)}
                    disabled={!currentPage || currentPage <= 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>

                  <span className="text-sm">
                    Page {currentPage || 1} of {totalPages}
                  </span>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange((currentPage || 1) + 1)}
                    disabled={!currentPage || currentPage >= totalPages}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};
