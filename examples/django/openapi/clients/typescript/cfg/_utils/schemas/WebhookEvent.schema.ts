/**
 * Zod schema for WebhookEvent
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for individual webhook event.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for individual webhook event.
 */
export const WebhookEventSchema = z.object({
  id: z.number().int(),
  provider: z.string().max(50),
  event_type: z.string().max(100),
  status: z.nativeEnum(Enums.WebhookEventStatus),
  timestamp: z.string().datetime(),
  payload_size: z.number().int(),
  response_time: z.number().int(),
  retry_count: z.number().int().optional(),
  error_message: z.string().max(500).optional(),
  payload_preview: z.string().max(200).optional(),
  response_status_code: z.number().int().optional(),
  webhook_url: z.string().url().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WebhookEvent = z.infer<typeof WebhookEventSchema>