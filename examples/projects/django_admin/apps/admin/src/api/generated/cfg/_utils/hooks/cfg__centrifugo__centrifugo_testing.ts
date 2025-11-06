/**
 * SWR Hooks for Centrifugo Testing
 *
 * React hooks powered by SWR for data fetching with automatic caching,
 * revalidation, and optimistic updates.
 *
 * Usage:
 * ```typescript
 * // Query hooks (GET)
 * const { data, error, isLoading } = useUsers({ page: 1 })
 *
 * // Mutation hooks (POST/PUT/PATCH/DELETE)
 * const createUser = useCreateUser()
 * await createUser({ name: 'John', email: 'john@example.com' })
 * ```
 */
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/cfg__centrifugo__centrifugo_testing'
import type { API } from '../../index'
import type { ManualAckRequestRequest } from '../schemas/ManualAckRequestRequest.schema'
import type { ManualAckResponse } from '../schemas/ManualAckResponse.schema'
import type { PublishTestRequestRequest } from '../schemas/PublishTestRequestRequest.schema'
import type { PublishTestResponse } from '../schemas/PublishTestResponse.schema'

/**
 * Publish test message
 *
 * @method POST
 * @path /cfg/centrifugo/testing/publish-test/
 */
export function useCreateCentrifugoTestingPublishTestCreate() {
  const { mutate } = useSWRConfig()

  return async (data: PublishTestRequestRequest, client?: API): Promise<PublishTestResponse> => {
    const result = await Fetchers.createCentrifugoTestingPublishTestCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-testing-publish-test')
    return result
  }
}


/**
 * Publish with database logging
 *
 * @method POST
 * @path /cfg/centrifugo/testing/publish-with-logging/
 */
export function useCreateCentrifugoTestingPublishWithLoggingCreate() {
  const { mutate } = useSWRConfig()

  return async (data: PublishTestRequestRequest, client?: API): Promise<PublishTestResponse> => {
    const result = await Fetchers.createCentrifugoTestingPublishWithLoggingCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-testing-publish-with-logging')
    return result
  }
}


/**
 * Send manual ACK
 *
 * @method POST
 * @path /cfg/centrifugo/testing/send-ack/
 */
export function useCreateCentrifugoTestingSendAckCreate() {
  const { mutate } = useSWRConfig()

  return async (data: ManualAckRequestRequest, client?: API): Promise<ManualAckResponse> => {
    const result = await Fetchers.createCentrifugoTestingSendAckCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-testing-send-ack')
    return result
  }
}


