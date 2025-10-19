/**
 * Zod schema for PatchedDocumentArchiveRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Document archive serializer.
 *  */
import { z } from 'zod'

/**
 * Document archive serializer.
 */
export const PatchedDocumentArchiveRequestSchema = z.object({
  title: z.string().min(1).max(512).optional(),
  description: z.string().optional(),
  is_public: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedDocumentArchiveRequest = z.infer<typeof PatchedDocumentArchiveRequestSchema>