/**
 * Zod schema for DocumentRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Document response serializer.
 *  */
import { z } from 'zod'

/**
 * Document response serializer.
 */
export const DocumentRequestSchema = z.object({
  title: z.string().min(1).max(512),
  file_type: z.string().min(1).max(100).optional(),
  file_size: z.int().min(0.0).max(2147483647.0).optional(),
  metadata: z.record(z.string(), z.any()).nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DocumentRequest = z.infer<typeof DocumentRequestSchema>