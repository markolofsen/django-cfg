/**
 * Zod schema for PostList
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for post list view.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { AuthorSchema } from './Author.schema'
import { BlogCategorySchema } from './BlogCategory.schema'
import { TagSchema } from './Tag.schema'

/**
 * Serializer for post list view.
 */
export const PostListSchema = z.object({
  id: z.number().int(),
  title: z.string().max(200),
  slug: z.string().max(200).regex(/^[-a-zA-Z0-9_]+$/).optional(),
  excerpt: z.string().max(500).optional(),
  author: AuthorSchema,
  category: BlogCategorySchema,
  tags: z.array(TagSchema),
  status: z.nativeEnum(Enums.PostListStatus).optional(),
  is_featured: z.boolean().optional(),
  featured_image: z.string().url().optional(),
  featured_image_alt: z.string().max(255).optional(),
  views_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  likes_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  comments_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  shares_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  published_at: z.string().datetime().optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PostList = z.infer<typeof PostListSchema>