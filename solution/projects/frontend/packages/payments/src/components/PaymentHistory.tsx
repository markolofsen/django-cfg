'use client';

// ============================================================================
// @djangocfg/payments — PaymentHistory
// ============================================================================
// A sortable table of PaymentRecord rows, built on the ui-core Table
// primitives. Pure presentational — the host feeds `records` (e.g. from
// usePaymentHistory()).
//
// This deliberately does NOT use a generic data-grid. A package may not depend
// on a widget (see widgets/CLAUDE.md), and the two sortable columns here are
// the whole requirement; a grid would buy filtering, pagination and selection
// that this surface never shows.

import React, { useCallback, useMemo, useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@djangocfg/ui-core';
import { PaymentStatusBadge } from './PaymentStatusBadge';
import { formatAmount } from '../domain/money';
import type { PaymentRecord } from '../domain/types';

type SortKey = 'createdAt' | 'amount';
type SortDirection = 'asc' | 'desc';

interface SortState {
  key: SortKey;
  direction: SortDirection;
}

export interface PaymentHistoryProps {
  records: PaymentRecord[];
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (record: PaymentRecord) => void;
  locale?: string;
  className?: string;
}

const SORT_INDICATOR: Record<SortDirection, string> = { asc: '↑', desc: '↓' };

export function PaymentHistory({
  records,
  loading,
  emptyMessage = 'No payments yet.',
  onRowClick,
  locale,
  className,
}: PaymentHistoryProps) {
  const [sort, setSort] = useState<SortState>({ key: 'createdAt', direction: 'desc' });

  const toggleSort = useCallback((key: SortKey) => {
    setSort((current) =>
      current.key === key
        ? { key, direction: current.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: 'desc' },
    );
  }, []);

  const sortedRecords = useMemo(() => {
    const factor = sort.direction === 'asc' ? 1 : -1;
    // Sort a copy: `records` belongs to the host and may be memoized upstream.
    return [...records].sort((a, b) => {
      if (sort.key === 'amount') return (a.amount - b.amount) * factor;
      return (Date.parse(a.createdAt) - Date.parse(b.createdAt)) * factor;
    });
  }, [records, sort]);

  const rows = useMemo(
    () =>
      sortedRecords.map((record) => ({
        record,
        id: record.id,
        date: new Date(record.createdAt).toLocaleDateString(locale),
        reference: `${record.reference.kind} · ${record.reference.id}`,
        amount: formatAmount(record.amount, record.currency, locale),
      })),
    [sortedRecords, locale],
  );

  const renderSortableHead = (key: SortKey, label: string) => (
    <TableHead>
      <button
        type="button"
        onClick={() => toggleSort(key)}
        className="inline-flex items-center gap-1 font-medium hover:text-foreground"
        aria-sort={sort.key === key ? (sort.direction === 'asc' ? 'ascending' : 'descending') : 'none'}
      >
        {label}
        {sort.key === key ? <span aria-hidden>{SORT_INDICATOR[sort.direction]}</span> : null}
      </button>
    </TableHead>
  );

  return (
    <div className={className}>
      <Table>
        <TableHeader>
          <TableRow>
            {renderSortableHead('createdAt', 'Date')}
            <TableHead>For</TableHead>
            {renderSortableHead('amount', 'Amount')}
            <TableHead>Provider</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {loading || rows.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="py-8 text-center text-muted-foreground">
                {loading ? 'Loading…' : emptyMessage}
              </TableCell>
            </TableRow>
          ) : (
            rows.map((row) => (
              <TableRow
                key={row.id}
                onClick={onRowClick ? () => onRowClick(row.record) : undefined}
                className={onRowClick ? 'cursor-pointer' : undefined}
              >
                <TableCell>{row.date}</TableCell>
                <TableCell>{row.reference}</TableCell>
                <TableCell>{row.amount}</TableCell>
                <TableCell>{row.record.provider}</TableCell>
                <TableCell>
                  <PaymentStatusBadge status={row.record.status} />
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
