/**
 * Zod schema for UserProfileUpdateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for updating user profiles.
 *  */
import { z } from 'zod'

/**
 * Serializer for updating user profiles.
 */
export const UserProfileUpdateRequestSchema = z.object({
  website: z.string().url().max(200).optional(),
  github: z.string().max(100).optional(),
  twitter: z.string().max(100).optional(),
  linkedin: z.string().max(100).optional(),
  company: z.string().max(100).optional(),
  job_title: z.string().max(100).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type UserProfileUpdateRequest = z.infer<typeof UserProfileUpdateRequestSchema>