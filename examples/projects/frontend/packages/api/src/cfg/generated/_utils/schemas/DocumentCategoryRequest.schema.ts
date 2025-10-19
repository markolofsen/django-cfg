/**
 * Zod schema for DocumentCategoryRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Document category serializer.
 *  */
import { z } from 'zod'

/**
 * Document category serializer.
 */
export const DocumentCategoryRequestSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  is_public: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DocumentCategoryRequest = z.infer<typeof DocumentCategoryRequestSchema>