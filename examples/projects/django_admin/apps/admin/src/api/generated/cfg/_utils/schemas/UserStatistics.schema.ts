/**
 * Zod schema for UserStatistics
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for user statistics.
 *  */
import { z } from 'zod'

/**
 * Serializer for user statistics.
 */
export const UserStatisticsSchema = z.object({
  total_users: z.int(),
  active_users: z.int(),
  new_users: z.int(),
  superusers: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type UserStatistics = z.infer<typeof UserStatisticsSchema>