/**
 * Typed fetchers for Centrifugo Testing
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
import { ConnectionTokenRequestRequestSchema, type ConnectionTokenRequestRequest } from '../schemas/ConnectionTokenRequestRequest.schema'
import { ConnectionTokenResponseSchema, type ConnectionTokenResponse } from '../schemas/ConnectionTokenResponse.schema'
import { ManualAckRequestRequestSchema, type ManualAckRequestRequest } from '../schemas/ManualAckRequestRequest.schema'
import { ManualAckResponseSchema, type ManualAckResponse } from '../schemas/ManualAckResponse.schema'
import { PublishTestRequestRequestSchema, type PublishTestRequestRequest } from '../schemas/PublishTestRequestRequest.schema'
import { PublishTestResponseSchema, type PublishTestResponse } from '../schemas/PublishTestResponse.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Generate connection token
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/testing/connection-token/
 */
export async function createCentrifugoAdminApiTestingConnectionTokenCreate(  data: ConnectionTokenRequestRequest,  client?: API
): Promise<ConnectionTokenResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.centrifugoAdminApiTestingConnectionTokenCreate(data)
  return ConnectionTokenResponseSchema.parse(response)
}


/**
 * Publish test message
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/testing/publish-test/
 */
export async function createCentrifugoAdminApiTestingPublishTestCreate(  data: PublishTestRequestRequest,  client?: API
): Promise<PublishTestResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.centrifugoAdminApiTestingPublishTestCreate(data)
  return PublishTestResponseSchema.parse(response)
}


/**
 * Publish with database logging
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/testing/publish-with-logging/
 */
export async function createCentrifugoAdminApiTestingPublishWithLoggingCreate(  data: PublishTestRequestRequest,  client?: API
): Promise<PublishTestResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.centrifugoAdminApiTestingPublishWithLoggingCreate(data)
  return PublishTestResponseSchema.parse(response)
}


/**
 * Send manual ACK
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/testing/send-ack/
 */
export async function createCentrifugoAdminApiTestingSendAckCreate(  data: ManualAckRequestRequest,  client?: API
): Promise<ManualAckResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.centrifugoAdminApiTestingSendAckCreate(data)
  return ManualAckResponseSchema.parse(response)
}


/**
 * Generate connection token
 *
 * @method POST
 * @path /cfg/centrifugo/testing/connection-token/
 */
export async function createCentrifugoTestingConnectionTokenCreate(  data: ConnectionTokenRequestRequest,  client?: API
): Promise<ConnectionTokenResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.connectionTokenCreate(data)
  return ConnectionTokenResponseSchema.parse(response)
}


/**
 * Publish test message
 *
 * @method POST
 * @path /cfg/centrifugo/testing/publish-test/
 */
export async function createCentrifugoTestingPublishTestCreate(  data: PublishTestRequestRequest,  client?: API
): Promise<PublishTestResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.publishTestCreate(data)
  return PublishTestResponseSchema.parse(response)
}


/**
 * Publish with database logging
 *
 * @method POST
 * @path /cfg/centrifugo/testing/publish-with-logging/
 */
export async function createCentrifugoTestingPublishWithLoggingCreate(  data: PublishTestRequestRequest,  client?: API
): Promise<PublishTestResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.publishWithLoggingCreate(data)
  return PublishTestResponseSchema.parse(response)
}


/**
 * Send manual ACK
 *
 * @method POST
 * @path /cfg/centrifugo/testing/send-ack/
 */
export async function createCentrifugoTestingSendAckCreate(  data: ManualAckRequestRequest,  client?: API
): Promise<ManualAckResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.sendAckCreate(data)
  return ManualAckResponseSchema.parse(response)
}


