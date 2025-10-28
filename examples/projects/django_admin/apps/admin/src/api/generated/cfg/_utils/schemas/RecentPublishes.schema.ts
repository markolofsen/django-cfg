/**
 * Zod schema for RecentPublishes
 *
 * This schema provides runtime validation and type inference.
 *  * Recent publishes list.
 *  */
import { z } from 'zod'

/**
 * Recent publishes list.
 */
export const RecentPublishesSchema = z.object({
  publishes: z.array(z.record(z.string(), z.any())),
  count: z.int(),
  total_available: z.int(),
  offset: z.int().optional(),
  has_more: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RecentPublishes = z.infer<typeof RecentPublishesSchema>