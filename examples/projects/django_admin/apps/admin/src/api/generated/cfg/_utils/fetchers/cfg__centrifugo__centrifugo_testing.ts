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
import { consola } from 'consola'
import { ManualAckRequestRequestSchema, type ManualAckRequestRequest } from '../schemas/ManualAckRequestRequest.schema'
import { ManualAckResponseSchema, type ManualAckResponse } from '../schemas/ManualAckResponse.schema'
import { PublishTestRequestRequestSchema, type PublishTestRequestRequest } from '../schemas/PublishTestRequestRequest.schema'
import { PublishTestResponseSchema, type PublishTestResponse } from '../schemas/PublishTestResponse.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Publish test message
 *
 * @method POST
 * @path /cfg/centrifugo/testing/publish-test/
 */
export async function createCentrifugoTestingPublishTestCreate(  data: PublishTestRequestRequest,  client?: any
): Promise<PublishTestResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.publishTestCreate(data)
  try {
    return PublishTestResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createCentrifugoTestingPublishTestCreate',
      message: `Path: /cfg/centrifugo/testing/publish-test/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Publish with database logging
 *
 * @method POST
 * @path /cfg/centrifugo/testing/publish-with-logging/
 */
export async function createCentrifugoTestingPublishWithLoggingCreate(  data: PublishTestRequestRequest,  client?: any
): Promise<PublishTestResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.publishWithLoggingCreate(data)
  try {
    return PublishTestResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createCentrifugoTestingPublishWithLoggingCreate',
      message: `Path: /cfg/centrifugo/testing/publish-with-logging/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Send manual ACK
 *
 * @method POST
 * @path /cfg/centrifugo/testing/send-ack/
 */
export async function createCentrifugoTestingSendAckCreate(  data: ManualAckRequestRequest,  client?: any
): Promise<ManualAckResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_testing.sendAckCreate(data)
  try {
    return ManualAckResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createCentrifugoTestingSendAckCreate',
      message: `Path: /cfg/centrifugo/testing/send-ack/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


