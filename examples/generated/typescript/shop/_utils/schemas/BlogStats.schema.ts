/**
 * Zod schema for BlogStats
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for blog statistics.
 *  */
import { z } from 'zod'
import { BlogCategorySchema } from './BlogCategory.schema'
import { PostListSchema } from './PostList.schema'
import { TagSchema } from './Tag.schema'

/**
 * Serializer for blog statistics.
 */
export const BlogStatsSchema = z.object({
  total_posts: z.number().int(),
  published_posts: z.number().int(),
  draft_posts: z.number().int(),
  total_comments: z.number().int(),
  total_views: z.number().int(),
  total_likes: z.number().int(),
  popular_posts: z.array(PostListSchema),
  recent_posts: z.array(PostListSchema),
  top_categories: z.array(BlogCategorySchema),
  top_tags: z.array(TagSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type BlogStats = z.infer<typeof BlogStatsSchema>