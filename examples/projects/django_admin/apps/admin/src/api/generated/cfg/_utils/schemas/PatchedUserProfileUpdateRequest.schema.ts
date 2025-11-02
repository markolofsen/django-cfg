/**
 * Zod schema for PatchedUserProfileUpdateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for updating user profile.
 *  */
import { z } from 'zod'

/**
 * Serializer for updating user profile.
 */
export const PatchedUserProfileUpdateRequestSchema = z.object({
  first_name: z.string().max(50).optional(),
  last_name: z.string().max(50).optional(),
  company: z.string().max(100).optional(),
  phone: z.string().max(20).optional(),
  position: z.string().max(100).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedUserProfileUpdateRequest = z.infer<typeof PatchedUserProfileUpdateRequestSchema>