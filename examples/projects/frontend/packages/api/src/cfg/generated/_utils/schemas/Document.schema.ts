/**
 * Zod schema for Document
 *
 * This schema provides runtime validation and type inference.
 *  * Document response serializer.
 *  */
import { z } from 'zod'

/**
 * Document response serializer.
 */
export const DocumentSchema = z.object({
  id: z.uuid(),
  title: z.string().max(512),
  file_type: z.string().max(100).optional(),
  file_size: z.int().min(0.0).max(2147483647.0).optional(),
  processing_status: z.string(),
  chunks_count: z.int(),
  total_tokens: z.int(),
  total_cost_usd: z.number(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
  processing_started_at: z.iso.datetime(),
  processing_completed_at: z.iso.datetime(),
  processing_error: z.string(),
  metadata: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Document = z.infer<typeof DocumentSchema>