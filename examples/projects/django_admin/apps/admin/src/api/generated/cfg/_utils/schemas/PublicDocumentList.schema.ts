/**
 * Zod schema for PublicDocumentList
 *
 * This schema provides runtime validation and type inference.
 *  * Public document list serializer - minimal fields for listing.
 *  */
import { z } from 'zod'
import { PublicCategorySchema } from './PublicCategory.schema'

/**
 * Public document list serializer - minimal fields for listing.
 */
export const PublicDocumentListSchema = z.object({
  id: z.uuid(),
  title: z.string().max(512),
  category: PublicCategorySchema,
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PublicDocumentList = z.infer<typeof PublicDocumentListSchema>