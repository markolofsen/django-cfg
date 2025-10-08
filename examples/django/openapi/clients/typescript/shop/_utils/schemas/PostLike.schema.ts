/**
 * Zod schema for PostLike
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for post likes.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { AuthorSchema } from './Author.schema'

/**
 * Serializer for post likes.
 */
export const PostLikeSchema = z.object({
  id: z.number().int(),
  user: AuthorSchema,
  reaction: z.nativeEnum(Enums.PostLikeReaction).optional(),
  created_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PostLike = z.infer<typeof PostLikeSchema>