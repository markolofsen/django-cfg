/**
 * Zod schema for ShopCategory
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for shop categories.
 *  */
import { z } from 'zod'

/**
 * Serializer for shop categories.
 */
export const ShopCategorySchema = z.object({
  id: z.number().int(),
  name: z.string().max(100),
  slug: z.string().regex(/^[-a-zA-Z0-9_]+$/),
  description: z.string().optional(),
  image: z.string().url().optional(),
  parent: z.number().int().optional(),
  meta_title: z.string().max(60).optional(),
  meta_description: z.string().max(160).optional(),
  products_count: z.number().int(),
  children: z.array(z.record(z.string(), z.any())),
  is_active: z.boolean().optional(),
  sort_order: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ShopCategory = z.infer<typeof ShopCategorySchema>