/**
 * Generated API Client
 * Auto-generated thin wrapper - DO NOT EDIT
 */

import { CentrifugoRPCClient } from './rpc-client';
import type {
  HealthCheckParams,
  HealthCheckResult,
  UserPresenceParams,
  UserPresenceResult,
} from './types';

export class APIClient {
  constructor(private rpc: CentrifugoRPCClient) {}

  /**
   * Check system health status.
   */
  async systemHealth(params: HealthCheckParams): Promise<HealthCheckResult> {
    return this.rpc.call<HealthCheckResult>('system.health', params);
  }

  /**
   * Update user presence status.
   */
  async usersUpdatePresence(params: UserPresenceParams): Promise<UserPresenceResult> {
    return this.rpc.call<UserPresenceResult>('users.update_presence', params);
  }

}