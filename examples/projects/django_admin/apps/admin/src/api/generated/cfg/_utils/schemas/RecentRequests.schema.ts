/**
 * Zod schema for RecentRequests
 *
 * This schema provides runtime validation and type inference.
 *  * Recent gRPC requests list.
 *  */
import { z } from 'zod'

/**
 * Recent gRPC requests list.
 */
export const RecentRequestsSchema = z.object({
  requests: z.array(z.record(z.string(), z.any())),
  count: z.int(),
  total_available: z.int(),
  offset: z.int().optional(),
  has_more: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RecentRequests = z.infer<typeof RecentRequestsSchema>