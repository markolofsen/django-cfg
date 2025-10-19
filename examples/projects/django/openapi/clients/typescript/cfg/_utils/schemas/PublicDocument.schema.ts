/**
 * Zod schema for PublicDocument
 *
 * This schema provides runtime validation and type inference.
 *  * Public document detail serializer - only essential data for clients.
 *  */
import { z } from 'zod'
import { PublicCategorySchema } from './PublicCategory.schema'

/**
 * Public document detail serializer - only essential data for clients.
 */
export const PublicDocumentSchema = z.object({
  id: z.uuid(),
  title: z.string().max(512),
  content: z.string(),
  category: PublicCategorySchema,
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PublicDocument = z.infer<typeof PublicDocumentSchema>