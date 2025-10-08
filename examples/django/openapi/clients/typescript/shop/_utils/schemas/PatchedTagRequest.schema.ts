/**
 * Zod schema for PatchedTagRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for blog tags.
 *  */
import { z } from 'zod'

/**
 * Serializer for blog tags.
 */
export const PatchedTagRequestSchema = z.object({
  name: z.string().min(1).max(50).optional(),
  description: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedTagRequest = z.infer<typeof PatchedTagRequestSchema>