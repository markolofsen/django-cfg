/**
 * Zod schema for PaginatedPublicDocumentListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { PublicDocumentListSchema } from './PublicDocumentList.schema'

export const PaginatedPublicDocumentListListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(PublicDocumentListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedPublicDocumentListList = z.infer<typeof PaginatedPublicDocumentListListSchema>