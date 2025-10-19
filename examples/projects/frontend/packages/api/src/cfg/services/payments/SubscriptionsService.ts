/**
 * Subscriptions Service (DEPRECATED)
 *
 * Subscriptions functionality has been removed in Payments v2.0
 * This service is kept as a stub for backward compatibility
 */

import { BaseClient } from '../../BaseClient';

const DEPRECATED_ERROR = 'Subscriptions feature has been removed in Payments v2.0';

export class SubscriptionsService extends BaseClient {
  /**
   * @deprecated Subscriptions removed in v2.0
   */
  static async list(): Promise<{
    success: boolean;
    subscriptions?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Subscriptions removed in v2.0
   */
  static async create(): Promise<{
    success: boolean;
    subscription?: never;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Subscriptions removed in v2.0
   */
  static async get(): Promise<{
    success: boolean;
    subscription?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Subscriptions removed in v2.0
   */
  static async update(): Promise<{
    success: boolean;
    subscription?: never;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Subscriptions removed in v2.0
   */
  static async delete(): Promise<{
    success: boolean;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Subscriptions removed in v2.0
   */
  static async getAnalytics(): Promise<{
    success: boolean;
    analytics?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Subscriptions removed in v2.0
   */
  static async listTariffs(): Promise<{
    success: boolean;
    tariffs?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Subscriptions removed in v2.0
   */
  static async getTariff(): Promise<{
    success: boolean;
    tariff?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }
}
