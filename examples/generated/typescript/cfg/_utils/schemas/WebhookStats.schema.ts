/**
 * Zod schema for WebhookStats
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for webhook statistics response.
 *  */
import { z } from 'zod'

/**
 * Serializer for webhook statistics response.
 */
export const WebhookStatsSchema = z.object({
  total_webhooks: z.number().int(),
  successful_webhooks: z.number().int(),
  failed_webhooks: z.number().int(),
  success_rate: z.number(),
  providers: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WebhookStats = z.infer<typeof WebhookStatsSchema>