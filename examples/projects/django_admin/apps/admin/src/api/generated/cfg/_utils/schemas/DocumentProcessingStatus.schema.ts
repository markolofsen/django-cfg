/**
 * Zod schema for DocumentProcessingStatus
 *
 * This schema provides runtime validation and type inference.
 *  * Document processing status serializer.
 *  */
import { z } from 'zod'

/**
 * Document processing status serializer.
 */
export const DocumentProcessingStatusSchema = z.object({
  id: z.uuid(),
  status: z.string(),
  progress: z.record(z.string(), z.any()),
  error: z.string().nullable().optional(),
  processing_time_seconds: z.number().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DocumentProcessingStatus = z.infer<typeof DocumentProcessingStatusSchema>