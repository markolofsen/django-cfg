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
  id: z.int(),
  user: z.int(),
  user_info: z.record(z.string(), z.any()),
  website: z.url().optional(),
  github: z.string().max(100).optional(),
  twitter: z.string().max(100).optional(),
  linkedin: z.string().max(100).optional(),
  company: z.string().max(100).optional(),
  job_title: z.string().max(100).optional(),
  posts_count: z.int(),
  comments_count: z.int(),
  orders_count: z.int(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type UserProfile = z.infer<typeof UserProfileSchema>