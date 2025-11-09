/**
 * Zod schema for PaginatedPublishList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { PublishSchema } from './Publish.schema'

export const PaginatedPublishListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(PublishSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedPublishList = z.infer<typeof PaginatedPublishListSchema>