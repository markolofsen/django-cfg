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

export * from './shop__blog'
export * from './shop__blog__blog_categories'
export * from './shop__blog__blog_comments'
export * from './shop__blog__blog_posts'
export * from './shop__blog__blog_tags'
export * from './shop__shop__shop_categories'
export * from './shop__shop__shop_orders'
export * from './shop__shop__shop_products'
