/**
 * Typed Fetchers - Universal API functions
 *
 * Auto-generated from OpenAPI specification.
 * These functions work in any JavaScript environment.
 *
 * Features:
 * - Runtime validation with Zod
 * - Type-safe parameters and responses
 * - Works with any data-fetching library (SWR, React Query, etc)
 * - Server Component compatible
 *
 * Usage:
 * ```typescript
 * import * as fetchers from './fetchers'
 *
 * // Direct usage
 * const user = await fetchers.getUser(1)
 *
 * // With SWR
 * const { data } = useSWR('user-1', () => fetchers.getUser(1))
 *
 * // With React Query
 * const { data } = useQuery(['user', 1], () => fetchers.getUser(1))
 * ```
 */

export * from './cfg__accounts'
export * from './cfg__accounts__auth'
export * from './cfg__accounts__user_profile'
export * from './cfg__centrifugo'
export * from './cfg__centrifugo__centrifugo_admin_api'
export * from './cfg__centrifugo__centrifugo_monitoring'
export * from './cfg__centrifugo__centrifugo_testing'
export * from './cfg__dashboard__dashboard_activity'
export * from './cfg__dashboard__dashboard_api_zones'
export * from './cfg__dashboard__dashboard_charts'
export * from './cfg__dashboard__dashboard_commands'
export * from './cfg__dashboard__dashboard_overview'
export * from './cfg__dashboard__dashboard_statistics'
export * from './cfg__dashboard__dashboard_system'
export * from './cfg__endpoints'
export * from './cfg__health'
export * from './cfg__knowbase'
export * from './cfg__leads'
export * from './cfg__leads__lead_submission'
export * from './cfg__newsletter'
export * from './cfg__newsletter__bulk_email'
export * from './cfg__newsletter__campaigns'
export * from './cfg__newsletter__logs'
export * from './cfg__newsletter__newsletters'
export * from './cfg__newsletter__subscriptions'
export * from './cfg__newsletter__testing'
export * from './cfg__payments'
export * from './cfg__support'
export * from './cfg__tasks'
