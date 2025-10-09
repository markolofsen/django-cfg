/**
 * Zod schema for BlogCategory
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for blog categories.
 *  */
import { z } from 'zod'

/**
 * Serializer for blog categories.
 */
export const BlogCategorySchema = z.object({
  id: z.number().int(),
  name: z.string().max(100),
  slug: z.string().regex(/^[-a-zA-Z0-9_]+$/),
  description: z.string().optional(),
  color: z.string().max(7).optional(),
  meta_title: z.string().max(60).optional(),
  meta_description: z.string().max(160).optional(),
  parent: z.number().int().optional(),
  posts_count: z.number().int(),
  children: z.array(z.record(z.string(), z.any())),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type BlogCategory = z.infer<typeof BlogCategorySchema>