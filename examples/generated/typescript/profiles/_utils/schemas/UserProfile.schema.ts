/**
 * Zod schema for UserProfile
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for user profiles.
 *  */
import { z } from 'zod'

/**
 * Serializer for user profiles.
 */
export const UserProfileSchema = z.object({
  id: z.number().int(),
  user: z.number().int(),
  user_info: z.record(z.string(), z.any()),
  website: z.string().url().max(200).optional(),
  github: z.string().max(100).optional(),
  twitter: z.string().max(100).optional(),
  linkedin: z.string().max(100).optional(),
  company: z.string().max(100).optional(),
  job_title: z.string().max(100).optional(),
  posts_count: z.number().int(),
  comments_count: z.number().int(),
  orders_count: z.number().int(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type UserProfile = z.infer<typeof UserProfileSchema>