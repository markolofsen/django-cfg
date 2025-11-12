/**
 * Typed fetchers for Campaigns
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
import { NewsletterCampaignRequestSchema, type NewsletterCampaignRequest } from '../schemas/NewsletterCampaignRequest.schema'
import { PaginatedNewsletterCampaignListSchema, type PaginatedNewsletterCampaignList } from '../schemas/PaginatedNewsletterCampaignList.schema'
import { SendCampaignRequestSchema, type SendCampaignRequest } from '../schemas/SendCampaignRequest.schema'
import { SendCampaignResponseSchema, type SendCampaignResponse } from '../schemas/SendCampaignResponse.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List Newsletter Campaigns
 *
 * @method GET
 * @path /cfg/newsletter/campaigns/
 */
export async function getNewsletterCampaignsList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedNewsletterCampaignList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsList(params?.page, params?.page_size)
  try {
    return PaginatedNewsletterCampaignListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getNewsletterCampaignsList',
      message: `Path: /cfg/newsletter/campaigns/\nMethod: GET`,
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
            operation: 'getNewsletterCampaignsList',
            path: '/cfg/newsletter/campaigns/',
            method: 'GET',
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
 * Create Newsletter Campaign
 *
 * @method POST
 * @path /cfg/newsletter/campaigns/
 */
export async function createNewsletterCampaignsCreate(  data: NewsletterCampaignRequest,  client?: any
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsCreate(data)
  try {
    return NewsletterCampaignSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createNewsletterCampaignsCreate',
      message: `Path: /cfg/newsletter/campaigns/\nMethod: POST`,
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
            operation: 'createNewsletterCampaignsCreate',
            path: '/cfg/newsletter/campaigns/',
            method: 'POST',
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
 * Get Campaign Details
 *
 * @method GET
 * @path /cfg/newsletter/campaigns/{id}/
 */
export async function getNewsletterCampaignsRetrieve(  id: number,  client?: any
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsRetrieve(id)
  try {
    return NewsletterCampaignSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getNewsletterCampaignsRetrieve',
      message: `Path: /cfg/newsletter/campaigns/{id}/\nMethod: GET`,
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
            operation: 'getNewsletterCampaignsRetrieve',
            path: '/cfg/newsletter/campaigns/{id}/',
            method: 'GET',
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
 * Update Campaign
 *
 * @method PUT
 * @path /cfg/newsletter/campaigns/{id}/
 */
export async function updateNewsletterCampaignsUpdate(  id: number, data: NewsletterCampaignRequest,  client?: any
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsUpdate(id, data)
  try {
    return NewsletterCampaignSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateNewsletterCampaignsUpdate',
      message: `Path: /cfg/newsletter/campaigns/{id}/\nMethod: PUT`,
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
            operation: 'updateNewsletterCampaignsUpdate',
            path: '/cfg/newsletter/campaigns/{id}/',
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
 * Delete Campaign
 *
 * @method DELETE
 * @path /cfg/newsletter/campaigns/{id}/
 */
export async function deleteNewsletterCampaignsDestroy(  id: number,  client?: any
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsDestroy(id)
  return response
}


/**
 * Send Newsletter Campaign
 *
 * @method POST
 * @path /cfg/newsletter/campaigns/send/
 */
export async function createNewsletterCampaignsSendCreate(  data: SendCampaignRequest,  client?: any
): Promise<SendCampaignResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsSendCreate(data)
  try {
    return SendCampaignResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createNewsletterCampaignsSendCreate',
      message: `Path: /cfg/newsletter/campaigns/send/\nMethod: POST`,
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
            operation: 'createNewsletterCampaignsSendCreate',
            path: '/cfg/newsletter/campaigns/send/',
            method: 'POST',
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


