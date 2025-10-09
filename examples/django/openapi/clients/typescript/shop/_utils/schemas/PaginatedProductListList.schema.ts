/**
 * Zod schema for PaginatedProductListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { ProductListSchema } from './ProductList.schema'

export const PaginatedProductListListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional(),
  previous_page: z.number().int().optional(),
  results: z.array(ProductListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedProductListList = z.infer<typeof PaginatedProductListListSchema>