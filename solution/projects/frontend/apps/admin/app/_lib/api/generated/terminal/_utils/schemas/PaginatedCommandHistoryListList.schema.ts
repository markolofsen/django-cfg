/**
 * Zod schema for PaginatedCommandHistoryListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { CommandHistoryListSchema } from './CommandHistoryList.schema'

export const PaginatedCommandHistoryListListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(CommandHistoryListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedCommandHistoryListList = z.infer<typeof PaginatedCommandHistoryListListSchema>