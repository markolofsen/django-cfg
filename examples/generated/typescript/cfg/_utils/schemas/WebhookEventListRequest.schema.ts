/**
 * Zod schema for WebhookEventListRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for paginated webhook events list.
 *  */
import { z } from 'zod'
import { WebhookEventRequestSchema } from './WebhookEventRequest.schema'

/**
 * Serializer for paginated webhook events list.
 */
export const WebhookEventListRequestSchema = z.object({
  events: z.array(WebhookEventRequestSchema),
  total: z.number().int(),
  page: z.number().int(),
  per_page: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WebhookEventListRequest = z.infer<typeof WebhookEventListRequestSchema>