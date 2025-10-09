/**
 * Zod schema for PatchedCommentRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for blog comments.
 *  */
import { z } from 'zod'

/**
 * Serializer for blog comments.
 */
export const PatchedCommentRequestSchema = z.object({
  content: z.string().min(1).optional(),
  parent: z.number().int().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedCommentRequest = z.infer<typeof PatchedCommentRequestSchema>