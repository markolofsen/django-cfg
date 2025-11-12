/**
 * Typed fetchers for Newsletter
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
import { NewsletterCampaignSchema, type NewsletterCampaign } from '../schemas/NewsletterCampaign.schema'
import { PatchedNewsletterCampaignRequestSchema, type PatchedNewsletterCampaignRequest } from '../schemas/PatchedNewsletterCampaignRequest.schema'
import { PatchedUnsubscribeRequestSchema, type PatchedUnsubscribeRequest } from '../schemas/PatchedUnsubscribeRequest.schema'
import { UnsubscribeSchema, type Unsubscribe } from '../schemas/Unsubscribe.schema'
import { UnsubscribeRequestSchema, type UnsubscribeRequest } from '../schemas/UnsubscribeRequest.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/newsletter/campaigns/{id}/
 */
export async function partialUpdateNewsletterCampaignsPartialUpdate(  id: number, data?: PatchedNewsletterCampaignRequest,  client?: any
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()
  const response = await api.cfg_newsletter.campaignsPartialUpdate(id, data)
  try {
    return NewsletterCampaignSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateNewsletterCampaignsPartialUpdate',
      message: `Path: /cfg/newsletter/campaigns/{id}/\nMethod: PATCH`,
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

    // Dispatch browser CustomEvent (only if window is defined)
    if (typeof window !== 'undefined' && error instanceof Error && 'issues' in error) {
      try {
        const event = new CustomEvent('zod-validation-error', {
          detail: {
            operation: 'partialUpdateNewsletterCampaignsPartialUpdate',
            path: '/cfg/newsletter/campaigns/{id}/',
            method: 'PATCH',
            error: error,
            response: response,
            timestamp: new Date(),
          },
          bubbles: true,
          cancelable: false,
        });
        window.dispatchEvent(event);
      } catch (eventError) {
        // Silently fail - event dispatch should never crash the app
        consola.warn('Failed to dispatch validation error event:', eventError);
      }
    }

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/newsletter/unsubscribe/
 */
export async function updateNewsletterUnsubscribeUpdate(  data: UnsubscribeRequest,  client?: any
): Promise<Unsubscribe> {
  const api = client || getAPIInstance()
  const response = await api.cfg_newsletter.unsubscribeUpdate(data)
  try {
    return UnsubscribeSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateNewsletterUnsubscribeUpdate',
      message: `Path: /cfg/newsletter/unsubscribe/\nMethod: PUT`,
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

    // Dispatch browser CustomEvent (only if window is defined)
    if (typeof window !== 'undefined' && error instanceof Error && 'issues' in error) {
      try {
        const event = new CustomEvent('zod-validation-error', {
          detail: {
            operation: 'updateNewsletterUnsubscribeUpdate',
            path: '/cfg/newsletter/unsubscribe/',
            method: 'PUT',
            error: error,
            response: response,
            timestamp: new Date(),
          },
          bubbles: true,
          cancelable: false,
        });
        window.dispatchEvent(event);
      } catch (eventError) {
        // Silently fail - event dispatch should never crash the app
        consola.warn('Failed to dispatch validation error event:', eventError);
      }
    }

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/newsletter/unsubscribe/
 */
export async function partialUpdateNewsletterUnsubscribePartialUpdate(  data?: PatchedUnsubscribeRequest,  client?: any
): Promise<Unsubscribe> {
  const api = client || getAPIInstance()
  const response = await api.cfg_newsletter.unsubscribePartialUpdate(data)
  try {
    return UnsubscribeSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateNewsletterUnsubscribePartialUpdate',
      message: `Path: /cfg/newsletter/unsubscribe/\nMethod: PATCH`,
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

    // Dispatch browser CustomEvent (only if window is defined)
    if (typeof window !== 'undefined' && error instanceof Error && 'issues' in error) {
      try {
        const event = new CustomEvent('zod-validation-error', {
          detail: {
            operation: 'partialUpdateNewsletterUnsubscribePartialUpdate',
            path: '/cfg/newsletter/unsubscribe/',
            method: 'PATCH',
            error: error,
            response: response,
            timestamp: new Date(),
          },
          bubbles: true,
          cancelable: false,
        });
        window.dispatchEvent(event);
      } catch (eventError) {
        // Silently fail - event dispatch should never crash the app
        consola.warn('Failed to dispatch validation error event:', eventError);
      }
    }

    // Re-throw the error
    throw error;
  }
}


