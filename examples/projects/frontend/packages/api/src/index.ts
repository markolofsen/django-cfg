/**
 * @djangocfg/api - Complete API Package
 *
 * Auto-generated TypeScript API clients with JWT authentication and service layer
 *
 * Usage:
 * ```typescript
 * import { AuthService, LeadsService } from '@djangocfg/api';
 *
 * // Authenticate with OTP
 * const result = await AuthService.verifyOTP('user@example.com', '123456');
 * if (result.success) {
 *   console.log('Logged in:', result.user);
 * }
 *
 * // Use services
 * const leadsResult = await LeadsService.getLeads(1, 20);
 * if (leadsResult.success) {
 *   console.log('Leads:', leadsResult.data);
 * }
 *
 * // Logout
 * AuthService.logout();
 * ```
 */

// Export everything from generated SDK (types, enums, errors)
export * from './cfg/generated';

// Export API instance (advanced usage)
export { api } from './cfg/BaseClient';
export { api as default } from './cfg/BaseClient';

// Export all services (recommended usage)
export * from './cfg/services';

// Export all contexts (React contexts for data management)
export * from './cfg/contexts';

// Re-export all types and fetchers for convenience
// Usage: import { Schemas, Fetchers } from '@djangocfg/api'
export { Schemas, Fetchers } from './cfg/generated';

// Re-export commonly used types directly for convenience
// Usage: import type { User } from '@djangocfg/api'
export type {
  // Auth
  OTPRequestResponse,
  OTPVerifyResponse,
  User,
  // Add more types as needed
} from './cfg/generated/_utils/schemas';