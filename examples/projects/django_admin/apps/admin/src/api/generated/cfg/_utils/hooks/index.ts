/**
 * SWR Hooks - React data fetching hooks
 *
 * Auto-generated from OpenAPI specification.
 * Powered by SWR for automatic caching and revalidation.
 *
 * Features:
 * - Automatic caching and deduplication
 * - Revalidation on focus/reconnect
 * - Optimistic updates
 * - Type-safe parameters and responses
 *
 * Usage:
 * ```typescript
 * import * as hooks from './hooks'
 *
 * // Query hooks (GET)
 * const { data, error, isLoading } = hooks.useUsers({ page: 1 })
 *
 * // Mutation hooks (POST/PUT/PATCH/DELETE)
 * const createUser = hooks.useCreateUser()
 * await createUser({ name: 'John' })
 * ```
 */

export * from './cfg__accounts__auth'
export * from './cfg__newsletter__bulk_email'
export * from './cfg__newsletter__campaigns'
export * from './cfg__centrifugo__centrifugo_admin_api'
export * from './cfg__centrifugo__centrifugo_monitoring'
export * from './cfg__centrifugo__centrifugo_testing'
export * from './cfg__dashboard__dashboard_api_zones'
export * from './cfg__dashboard__dashboard_activity'
export * from './cfg__dashboard__dashboard_charts'
export * from './cfg__dashboard__dashboard_commands'
export * from './cfg__dashboard__dashboard_overview'
export * from './cfg__dashboard__dashboard_statistics'
export * from './cfg__dashboard__dashboard_system'
export * from './cfg__leads__lead_submission'
export * from './cfg__newsletter__logs'
export * from './cfg__newsletter__newsletters'
export * from './cfg__rq__rq_jobs'
export * from './cfg__rq__rq_monitoring'
export * from './cfg__rq__rq_queues'
export * from './cfg__rq__rq_registries'
export * from './cfg__rq__rq_schedules'
export * from './cfg__rq__rq_testing'
export * from './cfg__rq__rq_workers'
export * from './cfg__newsletter__subscriptions'
export * from './cfg__newsletter__testing'
export * from './cfg__accounts__user_profile'
export * from './cfg__accounts'
export * from './cfg__centrifugo'
export * from './cfg__endpoints'
export * from './cfg__grpc__grpc_monitoring'
export * from './cfg__health'
export * from './cfg__knowbase'
export * from './cfg__leads'
export * from './cfg__newsletter'
export * from './cfg__payments'
export * from './cfg__support'
