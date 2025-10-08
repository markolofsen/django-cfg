/**
 * Zod schema for PostDetailRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for post detail view.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for post detail view.
 */
export const PostDetailRequestSchema = z.object({
  title: z.string().min(1).max(200),
  slug: z.string().max(200).regex(/^[-a-zA-Z0-9_]+$/).optional(),
  content: z.string().min(1),
  excerpt: z.string().max(500).optional(),
  status: z.nativeEnum(Enums.PostDetailRequestStatus).optional(),
  is_featured: z.boolean().optional(),
  allow_comments: z.boolean().optional(),
  meta_title: z.string().max(60).optional(),
  meta_description: z.string().max(160).optional(),
  meta_keywords: z.string().max(255).optional(),
  featured_image: z.string().optional().nullable(),
  featured_image_alt: z.string().max(255).optional(),
  views_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  likes_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  comments_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  shares_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  published_at: z.string().datetime().optional().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PostDetailRequest = z.infer<typeof PostDetailRequestSchema>