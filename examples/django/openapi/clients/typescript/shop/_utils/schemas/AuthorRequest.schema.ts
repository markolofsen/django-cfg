/**
 * Zod schema for AuthorRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for post authors.
 *  */
import { z } from 'zod'

/**
 * Serializer for post authors.
 */
export const AuthorRequestSchema = z.object({
  username: z.string().min(1).max(150).regex(/^[\\w.@+-]+$/),
  first_name: z.string().max(50).optional(),
  last_name: z.string().max(50).optional(),
  avatar: z.string().optional().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type AuthorRequest = z.infer<typeof AuthorRequestSchema>