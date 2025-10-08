/**
 * Zod schema for TagRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for blog tags.
 *  */
import { z } from 'zod'

/**
 * Serializer for blog tags.
 */
export const TagRequestSchema = z.object({
  name: z.string().min(1).max(50),
  description: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TagRequest = z.infer<typeof TagRequestSchema>