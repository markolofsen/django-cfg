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

export * from './cfg__cfg__auth'
export * from './cfg__cfg__bulk_email'
export * from './cfg__cfg__campaigns'
export * from './cfg__cfg__cfg__accounts'
export * from './cfg__cfg__cfg__endpoints'
export * from './cfg__cfg__cfg__health'
export * from './cfg__cfg__cfg__leads'
export * from './cfg__cfg__cfg__newsletter'
export * from './cfg__cfg__cfg__payments'
export * from './cfg__cfg__cfg__support'
export * from './cfg__cfg__cfg__tasks'
export * from './cfg__cfg__lead_submission'
export * from './cfg__cfg__logs'
export * from './cfg__cfg__newsletters'
export * from './cfg__cfg__subscriptions'
export * from './cfg__cfg__testing'
export * from './cfg__cfg__user_profile'
export * from './cfg__cfg__webhooks'
