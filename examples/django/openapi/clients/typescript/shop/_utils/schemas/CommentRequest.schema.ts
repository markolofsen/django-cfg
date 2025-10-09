/**
 * Zod schema for CommentRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for blog comments.
 *  */
import { z } from 'zod'

/**
 * Serializer for blog comments.
 */
export const CommentRequestSchema = z.object({
  content: z.string().min(1),
  parent: z.number().int().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CommentRequest = z.infer<typeof CommentRequestSchema>