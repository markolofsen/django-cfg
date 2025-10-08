/**
 * Zod schema for PaginatedShopCategoryList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { ShopCategorySchema } from './ShopCategory.schema'

export const PaginatedShopCategoryListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional().nullable(),
  previous_page: z.number().int().optional().nullable(),
  results: z.array(ShopCategorySchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedShopCategoryList = z.infer<typeof PaginatedShopCategoryListSchema>