/**
 * Zod schema for PaginatedApiKeyList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { ApiKeySchema } from './ApiKey.schema'

export const PaginatedApiKeyListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(ApiKeySchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedApiKeyList = z.infer<typeof PaginatedApiKeyListSchema>