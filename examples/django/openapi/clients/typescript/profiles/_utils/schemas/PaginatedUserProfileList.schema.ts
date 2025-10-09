/**
 * Zod schema for PaginatedUserProfileList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { UserProfileSchema } from './UserProfile.schema'

export const PaginatedUserProfileListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional(),
  previous_page: z.number().int().optional(),
  results: z.array(UserProfileSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedUserProfileList = z.infer<typeof PaginatedUserProfileListSchema>