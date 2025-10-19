/**
 * Zod schema for DocumentArchiveDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Detailed archive serializer with items.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { ArchiveItemSchema } from './ArchiveItem.schema'
import { DocumentCategorySchema } from './DocumentCategory.schema'

/**
 * Detailed archive serializer with items.
 */
export const DocumentArchiveDetailSchema = z.object({
  id: z.uuid(),
  title: z.string().max(512),
  description: z.string().optional(),
  categories: z.array(DocumentCategorySchema),
  is_public: z.boolean().optional(),
  archive_file: z.url(),
  original_filename: z.string(),
  file_size: z.int(),
  archive_type: z.nativeEnum(Enums.DocumentArchiveDetailArchiveType),
  processing_status: z.nativeEnum(Enums.DocumentArchiveDetailProcessingStatus),
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
  items: z.array(ArchiveItemSchema),
  file_tree: z.record(z.string(), z.any()),
  metadata: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DocumentArchiveDetail = z.infer<typeof DocumentArchiveDetailSchema>