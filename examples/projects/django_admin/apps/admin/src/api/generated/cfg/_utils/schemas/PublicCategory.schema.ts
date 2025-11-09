/**
 * Zod schema for PublicCategory
 *
 * This schema provides runtime validation and type inference.
 *  * Public category serializer.
 *  */
import { z } from 'zod'

/**
 * Public category serializer.
 */
export const PublicCategorySchema = z.object({
  id: z.uuid(),
  name: z.string().max(255),
  description: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PublicCategory = z.infer<typeof PublicCategorySchema>