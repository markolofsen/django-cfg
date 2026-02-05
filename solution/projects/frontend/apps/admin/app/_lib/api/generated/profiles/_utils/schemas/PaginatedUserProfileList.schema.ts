/**
 * Zod schema for PaginatedUserProfileList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod';

import { UserProfileSchema } from './UserProfile.schema';

export const PaginatedUserProfileListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(UserProfileSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedUserProfileList = z.infer<typeof PaginatedUserProfileListSchema>