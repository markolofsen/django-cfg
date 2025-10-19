/**
 * Zod schema for DocumentCreateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Document creation request serializer.
 *  */
import { z } from 'zod'

/**
 * Document creation request serializer.
 */
export const DocumentCreateRequestSchema = z.object({
  title: z.string().min(1).max(512),
  content: z.string().min(10).max(1000000),
  file_type: z.string().min(1).optional(),
  metadata: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DocumentCreateRequest = z.infer<typeof DocumentCreateRequestSchema>