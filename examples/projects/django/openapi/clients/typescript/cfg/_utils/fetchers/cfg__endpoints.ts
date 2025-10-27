/**
 * Typed fetchers for Endpoints
 *
 * Universal functions that work in any environment:
 * - Next.js (App Router / Pages Router / Server Components)
 * - React Native
 * - Node.js backend
 *
 * These fetchers use Zod schemas for runtime validation.
 *
 * Usage:
 * ```typescript
 * // Configure API once (in your app entry point)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 *
 * // Then use fetchers anywhere
 * const users = await getUsers({ page: 1 })
 *
 * // With SWR
 * const { data } = useSWR(['users', params], () => getUsers(params))
 *
 * // With React Query
 * const { data } = useQuery(['users', params], () => getUsers(params))
 *
 * // In Server Component or SSR (pass custom client)
 * import { API } from '../../index'
 * const api = new API('https://api.example.com')
 * const users = await getUsers({ page: 1 }, api)
 * ```
 */
import { EndpointsStatusSchema, type EndpointsStatus } from '../schemas/EndpointsStatus.schema'
import { URLsListSchema, type URLsList } from '../schemas/URLsList.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/endpoints/drf/
 */
export async function getEndpointsDrfRetrieve(  client?: API
): Promise<EndpointsStatus> {
  const api = client || getAPIInstance()
  const response = await api.cfg_endpoints.drfRetrieve()
  return EndpointsStatusSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/endpoints/urls/
 */
export async function getEndpointsUrlsRetrieve(  client?: API
): Promise<URLsList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_endpoints.urlsRetrieve()
  return URLsListSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/endpoints/urls/compact/
 */
export async function getEndpointsUrlsCompactRetrieve(  client?: API
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_endpoints.urlsCompactRetrieve()
  return response
}


