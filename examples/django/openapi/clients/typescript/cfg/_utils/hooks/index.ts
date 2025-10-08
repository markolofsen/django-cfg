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

export * from './cfg__accounts__auth'
export * from './cfg__newsletter__bulk_email'
export * from './cfg__newsletter__campaigns'
export * from './cfg__leads__lead_submission'
export * from './cfg__newsletter__logs'
export * from './cfg__newsletter__newsletters'
export * from './cfg__newsletter__subscriptions'
export * from './cfg__newsletter__testing'
export * from './cfg__accounts__user_profile'
export * from './cfg__payments__webhooks'
export * from './cfg__accounts'
export * from './cfg__leads'
export * from './cfg__newsletter'
export * from './cfg__support'
export * from './cfg__payments'
export * from './cfg__tasks'
