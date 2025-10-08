/**
 * Zod schema for UserProfileStats
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for profile statistics.
 *  */
import { z } from 'zod'
import { UserProfileSchema } from './UserProfile.schema'

/**
 * Serializer for profile statistics.
 */
export const UserProfileStatsSchema = z.object({
  total_profiles: z.number().int(),
  profiles_with_company: z.number().int(),
  profiles_with_social_links: z.number().int(),
  most_active_users: z.array(UserProfileSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type UserProfileStats = z.infer<typeof UserProfileStatsSchema>