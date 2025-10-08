/**
 * Zod schema for PaginatedAPIKeyListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { APIKeyListSchema } from './APIKeyList.schema'

export const PaginatedAPIKeyListListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional().nullable(),
  previous_page: z.number().int().optional().nullable(),
  results: z.array(APIKeyListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedAPIKeyListList = z.infer<typeof PaginatedAPIKeyListListSchema>