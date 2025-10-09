/**
 * SWR Hooks - React hooks for data fetching
 *
 * Auto-generated from OpenAPI specification.
 * These hooks use SWR for data fetching and caching.
 *
 * Usage:
 * ```typescript
 * import { useShopProducts } from './_utils/hooks'
 *
 * function ProductsPage() {
 *   const { data, error } = useShopProducts({ page: 1 })
 *   if (error) return <Error />
 *   if (!data) return <Loading />
 *   return <ProductList products={data.results} />
 * }
 * ```
 */

export * from './cfg__cfg__auth'
export * from './cfg__cfg__bulk_email'
export * from './cfg__cfg__campaigns'
export * from './cfg__cfg__lead_submission'
export * from './cfg__cfg__logs'
export * from './cfg__cfg__newsletters'
export * from './cfg__cfg__subscriptions'
export * from './cfg__cfg__testing'
export * from './cfg__cfg__user_profile'
export * from './cfg__cfg__webhooks'
export * from './cfg__cfg__cfg__accounts'
export * from './cfg__cfg__cfg__endpoints'
export * from './cfg__cfg__cfg__health'
export * from './cfg__cfg__cfg__leads'
export * from './cfg__cfg__cfg__newsletter'
export * from './cfg__cfg__cfg__payments'
export * from './cfg__cfg__cfg__support'
export * from './cfg__cfg__cfg__tasks'
