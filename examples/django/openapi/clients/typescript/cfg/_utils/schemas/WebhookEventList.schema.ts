/**
 * Zod schema for WebhookEventList
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for paginated webhook events list.
 *  */
import { z } from 'zod'
import { WebhookEventSchema } from './WebhookEvent.schema'

/**
 * Serializer for paginated webhook events list.
 */
export const WebhookEventListSchema = z.object({
  events: z.array(WebhookEventSchema),
  total: z.number().int(),
  page: z.number().int(),
  per_page: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WebhookEventList = z.infer<typeof WebhookEventListSchema>