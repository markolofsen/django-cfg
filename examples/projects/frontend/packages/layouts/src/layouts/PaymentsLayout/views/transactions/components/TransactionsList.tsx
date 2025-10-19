/**
 * Transactions List Component (v2.0 - Simplified)
 * Display transaction history with balance changes
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
import { History, Search, Filter, RefreshCw, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import { useOverviewContext } from '@djangocfg/api/cfg/contexts';

export const TransactionsList: React.FC = () => {
  const {
    transactions,
    isLoadingTransactions,
    refreshTransactions,
  } = useOverviewContext();

  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  // Extract transactions array from response (handle different possible structures)
  const transactionsList = transactions?.results || transactions?.transactions || [];

  const formatCurrency = (amount?: number | null) => {
    if (amount === null || amount === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatDate = (date: string | null | undefined): string => {
    if (!date) return 'N/A';
    try {
      return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return 'Invalid date';
    }
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

  const getTypeVariant = (
    type: string | null | undefined
  ): 'default' | 'destructive' | 'outline' | 'secondary' => {
    switch (type?.toLowerCase()) {
      case 'deposit':
      case 'credit':
        return 'default';
      case 'withdrawal':
      case 'debit':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getTypeIcon = (type: string | null | undefined) => {
    const isDeposit = type?.toLowerCase() === 'deposit' || type?.toLowerCase() === 'credit';
    return isDeposit ? (
      <ArrowDownLeft className="h-4 w-4 text-green-600" />
    ) : (
      <ArrowUpRight className="h-4 w-4 text-red-600" />
    );
  };

  const handleSearch = async (value: string) => {
    setSearchTerm(value);
    await refreshTransactions();
  };

  const handleTypeFilter = async (type: string) => {
    setTypeFilter(type);
    await refreshTransactions();
  };

  // Filter transactions client-side
  const filteredTransactions = transactionsList.filter((transaction: any) => {
    const matchesSearch = searchTerm
      ? transaction.id?.toString().toLowerCase().includes(searchTerm.toLowerCase()) ||
        transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transaction.type?.toLowerCase().includes(searchTerm.toLowerCase())
      : true;

    const matchesType = typeFilter !== 'all'
      ? transaction.type?.toLowerCase() === typeFilter.toLowerCase()
      : true;

    return matchesSearch && matchesType;
  });

  if (isLoadingTransactions) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Transaction History
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between p-4 border rounded-sm">
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

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Transaction History
          </div>
          <Button variant="outline" size="sm" onClick={refreshTransactions} disabled={isLoadingTransactions}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoadingTransactions ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by ID, description, or type..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select value={typeFilter} onValueChange={handleTypeFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="deposit">Deposits</SelectItem>
              <SelectItem value="withdrawal">Withdrawals</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Transactions Table */}
        {filteredTransactions.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 bg-muted rounded-full flex items-center justify-center">
              <History className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No Transactions Found</h3>
            <p className="text-muted-foreground">
              {searchTerm || typeFilter !== 'all'
                ? 'No transactions match your current filters'
                : "You don't have any transactions yet"}
            </p>
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date & Time</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Balance After</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Reference</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTransactions.map((transaction: any, index: number) => {
                  const isDeposit = transaction.type?.toLowerCase() === 'deposit' || transaction.type?.toLowerCase() === 'credit';
                  return (
                    <TableRow key={transaction.id || index}>
                      <TableCell>
                        <div>
                          <div className="font-medium">
                            {formatDate(transaction.created_at || transaction.timestamp)}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {getRelativeTime(transaction.created_at || transaction.timestamp)}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getTypeIcon(transaction.type)}
                          <Badge variant={getTypeVariant(transaction.type)}>
                            {transaction.type || 'Unknown'}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono font-semibold">
                        <span className={isDeposit ? 'text-green-600' : 'text-red-600'}>
                          {isDeposit ? '+' : '-'}
                          {formatCurrency(Math.abs(transaction.amount || transaction.amount_usd || 0))}
                        </span>
                      </TableCell>
                      <TableCell className="font-mono">
                        {formatCurrency(transaction.balance_after || 0)}
                      </TableCell>
                      <TableCell className="text-sm">
                        {transaction.description || transaction.note || 'No description'}
                      </TableCell>
                      <TableCell className="font-mono text-sm text-muted-foreground">
                        {transaction.reference || transaction.payment_id
                          ? `${(transaction.reference || transaction.payment_id).toString().slice(0, 8)}...`
                          : 'N/A'}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
