/**
 * Zod schema for PaginatedDocumentArchiveListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { DocumentArchiveListSchema } from './DocumentArchiveList.schema'

export const PaginatedDocumentArchiveListListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(DocumentArchiveListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedDocumentArchiveListList = z.infer<typeof PaginatedDocumentArchiveListListSchema>