/**
 * Zod schema for UserProfileRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for user profiles.
 *  */
import { z } from 'zod'

/**
 * Serializer for user profiles.
 */
export const UserProfileRequestSchema = z.object({
  website: z.union([z.url(), z.literal('')]).optional(),
  github: z.string().max(100).optional(),
  twitter: z.string().max(100).optional(),
  linkedin: z.string().max(100).optional(),
  company: z.string().max(100).optional(),
  job_title: z.string().max(100).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type UserProfileRequest = z.infer<typeof UserProfileRequestSchema>