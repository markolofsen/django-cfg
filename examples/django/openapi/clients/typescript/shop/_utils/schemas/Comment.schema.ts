/**
 * Zod schema for Comment
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for blog comments.
 *  */
import { z } from 'zod'
import { AuthorSchema } from './Author.schema'

/**
 * Serializer for blog comments.
 */
export const CommentSchema = z.object({
  id: z.number().int(),
  content: z.string(),
  author: AuthorSchema,
  parent: z.number().int().optional(),
  is_approved: z.boolean(),
  likes_count: z.number().int(),
  replies: z.array(z.record(z.string(), z.any())),
  can_edit: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Comment = z.infer<typeof CommentSchema>