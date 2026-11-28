'use client';

// ============================================================================
// @djangocfg/payments — usePaymentHistory
// ============================================================================
// Loads paginated payment records via the injected adapter's optional
// listPayments(). Returns an empty list (not an error) when the adapter
// doesn't support history.

import { useCallback, useEffect, useState } from 'react';
import { usePaymentAdapter } from '../context/PaymentProvider';
import type { PaymentRecord } from '../domain/types';

export interface UsePaymentHistoryResult {
  records: PaymentRecord[];
  loading: boolean;
  error: string | null;
  nextCursor: string | null;
  /** Reload from the start. */
  refresh: () => Promise<void>;
  /** Append the next page (if any). */
  loadMore: () => Promise<void>;
  /** Whether the adapter supports history at all. */
  supported: boolean;
}

export interface UsePaymentHistoryProps {
  limit?: number;
  /** Load on mount. Default true. */
  autoLoad?: boolean;
}

export function usePaymentHistory(
  { limit, autoLoad = true }: UsePaymentHistoryProps = {},
): UsePaymentHistoryResult {
  const adapter = usePaymentAdapter();
  const supported = typeof adapter.listPayments === 'function';

  const [records, setRecords] = useState<PaymentRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!adapter.listPayments) return;
    setLoading(true);
    setError(null);
    try {
      const page = await adapter.listPayments({ limit });
      setRecords(page.items);
      setNextCursor(page.nextCursor ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load payments.');
    } finally {
      setLoading(false);
    }
  }, [adapter, limit]);

  const loadMore = useCallback(async () => {
    if (!adapter.listPayments || !nextCursor) return;
    setLoading(true);
    setError(null);
    try {
      const page = await adapter.listPayments({ limit, cursor: nextCursor });
      setRecords((prev) => [...prev, ...page.items]);
      setNextCursor(page.nextCursor ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load payments.');
    } finally {
      setLoading(false);
    }
  }, [adapter, limit, nextCursor]);

  useEffect(() => {
    if (autoLoad && supported) void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoLoad, supported]);

  return { records, loading, error, nextCursor, refresh, loadMore, supported };
}
