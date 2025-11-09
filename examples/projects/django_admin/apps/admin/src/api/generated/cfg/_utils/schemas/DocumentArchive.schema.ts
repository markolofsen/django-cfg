/**
 * Zod schema for DocumentArchive
 *
 * This schema provides runtime validation and type inference.
 *  * Document archive serializer.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { DocumentCategorySchema } from './DocumentCategory.schema'

/**
 * Document archive serializer.
 */
export const DocumentArchiveSchema = z.object({
  id: z.uuid(),
  title: z.string().max(512),
  description: z.string().optional(),
  categories: z.array(DocumentCategorySchema),
  is_public: z.boolean().optional(),
  archive_file: z.url(),
  original_filename: z.string(),
  file_size: z.int(),
  archive_type: z.nativeEnum(Enums.DocumentArchiveArchiveType),
  processing_status: z.nativeEnum(Enums.DocumentArchiveProcessingStatus),
  processed_at: z.iso.datetime().nullable(),
  processing_duration_ms: z.int(),
  processing_error: z.string(),
  total_items: z.int(),
  processed_items: z.int(),
  total_chunks: z.int(),
  vectorized_chunks: z.int(),
  total_tokens: z.int(),
  total_cost_usd: z.number(),
  processing_progress: z.number(),
  vectorization_progress: z.number(),
  is_processed: z.boolean(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DocumentArchive = z.infer<typeof DocumentArchiveSchema>