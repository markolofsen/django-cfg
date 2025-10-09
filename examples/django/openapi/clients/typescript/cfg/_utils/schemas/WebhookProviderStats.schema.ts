/**
 * Zod schema for WebhookProviderStats
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for provider-specific webhook statistics.
 *  */
import { z } from 'zod'

/**
 * Serializer for provider-specific webhook statistics.
 */
export const WebhookProviderStatsSchema = z.object({
  total: z.number().int(),
  successful: z.number().int(),
  failed: z.number().int(),
  pending: z.number().int().optional(),
  success_rate: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WebhookProviderStats = z.infer<typeof WebhookProviderStatsSchema>