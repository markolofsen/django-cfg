/**
 * Zod schema for APIKeysOverview
 *
 * This schema provides runtime validation and type inference.
 *  * API keys overview metrics
 *  */
import { z } from 'zod'

/**
 * API keys overview metrics
 */
export const APIKeysOverviewSchema = z.object({
  total_keys: z.number().int(),
  active_keys: z.number().int(),
  expired_keys: z.number().int(),
  total_requests: z.number().int(),
  last_used_at: z.string().datetime().nullable(),
  most_used_key_name: z.string().nullable(),
  most_used_key_requests: z.number().int(),
  expiring_soon_count: z.number().int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIKeysOverview = z.infer<typeof APIKeysOverviewSchema>