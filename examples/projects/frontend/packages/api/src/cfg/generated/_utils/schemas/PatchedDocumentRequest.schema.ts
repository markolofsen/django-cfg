/**
 * Zod schema for PatchedDocumentRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Document response serializer.
 *  */
import { z } from 'zod'

/**
 * Document response serializer.
 */
export const PatchedDocumentRequestSchema = z.object({
  title: z.string().min(1).max(512).optional(),
  file_type: z.string().min(1).max(100).optional(),
  file_size: z.int().min(0.0).max(2147483647.0).optional(),
  metadata: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedDocumentRequest = z.infer<typeof PatchedDocumentRequestSchema>