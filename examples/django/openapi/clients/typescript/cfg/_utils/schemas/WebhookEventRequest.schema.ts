/**
 * Zod schema for WebhookEventRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for individual webhook event.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for individual webhook event.
 */
export const WebhookEventRequestSchema = z.object({
  provider: z.string().min(1).max(50),
  event_type: z.string().min(1).max(100),
  status: z.nativeEnum(Enums.WebhookEventRequestStatus),
  timestamp: z.string().datetime(),
  payload_size: z.number().int(),
  response_time: z.number().int(),
  retry_count: z.number().int().optional(),
  error_message: z.string().max(500).optional(),
  payload_preview: z.string().max(200).optional(),
  response_status_code: z.number().int().optional(),
  webhook_url: z.string().url().min(1).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WebhookEventRequest = z.infer<typeof WebhookEventRequestSchema>