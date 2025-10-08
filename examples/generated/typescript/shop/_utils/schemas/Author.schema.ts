/**
 * Zod schema for Author
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for post authors.
 *  */
import { z } from 'zod'

/**
 * Serializer for post authors.
 */
export const AuthorSchema = z.object({
  id: z.number().int(),
  username: z.string().max(150).regex(/^[\\w.@+-]+$/),
  first_name: z.string().max(50).optional(),
  last_name: z.string().max(50).optional(),
  full_name: z.string(),
  avatar: z.string().url().optional().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Author = z.infer<typeof AuthorSchema>