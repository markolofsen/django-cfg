/**
 * Zod schema for PaginatedDocumentList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { DocumentSchema } from './Document.schema'

export const PaginatedDocumentListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(DocumentSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedDocumentList = z.infer<typeof PaginatedDocumentListSchema>