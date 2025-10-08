/**
 * Zod schema for PostUpdate
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for post updates.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for post updates.
 */
export const PostUpdateSchema = z.object({
  title: z.string().max(200),
  content: z.string(),
  excerpt: z.string().max(500).optional(),
  category: z.number().int().optional().nullable(),
  tags: z.array(z.number().int()).optional(),
  status: z.nativeEnum(Enums.PostUpdateStatus).optional(),
  is_featured: z.boolean().optional(),
  allow_comments: z.boolean().optional(),
  meta_title: z.string().max(60).optional(),
  meta_description: z.string().max(160).optional(),
  meta_keywords: z.string().max(255).optional(),
  featured_image: z.string().url().optional().nullable(),
  featured_image_alt: z.string().max(255).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PostUpdate = z.infer<typeof PostUpdateSchema>