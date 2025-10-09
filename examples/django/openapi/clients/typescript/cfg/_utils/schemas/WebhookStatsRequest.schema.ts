/**
 * Zod schema for WebhookStatsRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for comprehensive webhook statistics.
 *  */
import { z } from 'zod'

/**
 * Serializer for comprehensive webhook statistics.
 */
export const WebhookStatsRequestSchema = z.object({
  total: z.number().int(),
  successful: z.number().int(),
  failed: z.number().int(),
  pending: z.number().int(),
  success_rate: z.number(),
  providers: z.record(z.string(), z.any()),
  last_24h: z.record(z.string(), z.any()),
  avg_response_time: z.number(),
  max_response_time: z.number().int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WebhookStatsRequest = z.infer<typeof WebhookStatsRequestSchema>