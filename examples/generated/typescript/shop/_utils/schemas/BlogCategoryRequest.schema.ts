/**
 * Zod schema for BlogCategoryRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for blog categories.
 *  */
import { z } from 'zod'

/**
 * Serializer for blog categories.
 */
export const BlogCategoryRequestSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional(),
  color: z.string().min(1).max(7).optional(),
  meta_title: z.string().max(60).optional(),
  meta_description: z.string().max(160).optional(),
  parent: z.number().int().optional().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type BlogCategoryRequest = z.infer<typeof BlogCategoryRequestSchema>