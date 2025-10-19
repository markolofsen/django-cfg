/**
 * Webhooks Service (DEPRECATED)
 *
 * Webhooks functionality has been integrated into main Payments API in v2.0
 * This service is kept as a stub for backward compatibility
 */

import { BaseClient } from '../../BaseClient';

const DEPRECATED_ERROR = 'Webhooks feature has been integrated into Payments API in v2.0';

export class WebhooksService extends BaseClient {
  /**
   * @deprecated Webhooks integrated into Payments API in v2.0
   */
  static async list(): Promise<{
    success: boolean;
    events?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Webhooks integrated into Payments API in v2.0
   */
  static async get(): Promise<{
    success: boolean;
    event?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Webhooks integrated into Payments API in v2.0
   */
  static async getStats(): Promise<{
    success: boolean;
    stats?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Webhooks integrated into Payments API in v2.0
   */
  static async getHealth(): Promise<{
    success: boolean;
    health?: never;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }

  /**
   * @deprecated Webhooks integrated into Payments API in v2.0
   */
  static async retry(): Promise<{
    success: boolean;
    error?: string;
  }> {
    return { success: false, error: DEPRECATED_ERROR };
  }
}
