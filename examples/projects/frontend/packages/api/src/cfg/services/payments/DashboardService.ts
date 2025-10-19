/**
 * Payment Dashboard Service (DEPRECATED)
 *
 * Dashboard functionality has been removed in Payments v2.0
 * Use basic endpoints (balance, payments, transactions) instead
 * This service is kept as a stub for backward compatibility
 */

import { BaseClient } from '../../BaseClient';

const DEPRECATED_ERROR = 'Dashboard feature has been removed in Payments v2.0. Use balance/payments/transactions endpoints instead';

export class PaymentDashboardService extends BaseClient {
  /**
   * @deprecated Dashboard removed in v2.0
   */
  static async getOverview(): Promise<{
    success: boolean;
    overview?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Dashboard removed in v2.0
   */
  static async getMetrics(): Promise<{
    success: boolean;
    metrics?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Dashboard removed in v2.0
   */
  static async getBalanceOverview(): Promise<{
    success: boolean;
    balance?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Dashboard removed in v2.0
   */
  static async getSubscriptionOverview(): Promise<{
    success: boolean;
    subscription?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Dashboard removed in v2.0
   */
  static async getApiKeysOverview(): Promise<{
    success: boolean;
    apiKeys?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Dashboard removed in v2.0
   */
  static async getChartData(): Promise<{
    success: boolean;
    chartData?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Dashboard removed in v2.0
   */
  static async getPaymentAnalytics(): Promise<{
    success: boolean;
    analytics?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Dashboard removed in v2.0
   */
  static async getRecentPayments(): Promise<{
    success: boolean;
    payments?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Dashboard removed in v2.0
   */
  static async getRecentTransactions(): Promise<{
    success: boolean;
    transactions?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }
}
