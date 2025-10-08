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

export * from './profiles'
