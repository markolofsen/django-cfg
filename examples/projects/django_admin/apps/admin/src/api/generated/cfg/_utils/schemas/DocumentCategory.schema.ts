/**
 * Zod schema for DocumentCategory
 *
 * This schema provides runtime validation and type inference.
 *  * Document category serializer.
 *  */
import { z } from 'zod'

/**
 * Document category serializer.
 */
export const DocumentCategorySchema = z.object({
  id: z.uuid(),
  name: z.string().max(255),
  description: z.string().optional(),
  is_public: z.boolean().optional(),
  created_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DocumentCategory = z.infer<typeof DocumentCategorySchema>