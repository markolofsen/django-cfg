/**
 * Zod schema for Tag
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for blog tags.
 *  */
import { z } from 'zod'

/**
 * Serializer for blog tags.
 */
export const TagSchema = z.object({
  id: z.number().int(),
  name: z.string().max(50),
  slug: z.string().regex(/^[-a-zA-Z0-9_]+$/),
  description: z.string().optional(),
  posts_count: z.number().int(),
  created_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Tag = z.infer<typeof TagSchema>