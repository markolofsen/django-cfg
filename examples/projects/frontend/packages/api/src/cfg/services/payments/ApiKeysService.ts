/**
 * API Keys Service (DEPRECATED)
 *
 * API Keys functionality has been removed in Payments v2.0
 * This service is kept as a stub for backward compatibility
 */

import { BaseClient } from '../../BaseClient';

const DEPRECATED_ERROR = 'API Keys feature has been removed in Payments v2.0';

export class ApiKeysService extends BaseClient {
  /**
   * @deprecated API Keys removed in v2.0
   */
  static async list(): Promise<{
    success: boolean;
    keys?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated API Keys removed in v2.0
   */
  static async create(): Promise<{
    success: boolean;
    key?: never;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated API Keys removed in v2.0
   */
  static async get(): Promise<{
    success: boolean;
    key?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated API Keys removed in v2.0
   */
  static async update(): Promise<{
    success: boolean;
    key?: never;
    error?: string;
    fieldErrors?: Record<string, string[]>;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated API Keys removed in v2.0
   */
  static async delete(): Promise<{
    success: boolean;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated API Keys removed in v2.0
   */
  static async validate(): Promise<{
    success: boolean;
    validation?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated API Keys removed in v2.0
   */
  static async getAnalytics(): Promise<{
    success: boolean;
    analytics?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated API Keys removed in v2.0
   */
  static async getStats(): Promise<{
    success: boolean;
    stats?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }
}
