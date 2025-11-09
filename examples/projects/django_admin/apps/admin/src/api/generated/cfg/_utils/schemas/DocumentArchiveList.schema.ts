/**
 * Zod schema for DocumentArchiveList
 *
 * This schema provides runtime validation and type inference.
 *  * Simplified archive serializer for list views.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { DocumentCategorySchema } from './DocumentCategory.schema'

/**
 * Simplified archive serializer for list views.
 */
export const DocumentArchiveListSchema = z.object({
  id: z.uuid(),
  title: z.string(),
  description: z.string(),
  categories: z.array(DocumentCategorySchema),
  is_public: z.boolean(),
  original_filename: z.string(),
  file_size: z.int(),
  archive_type: z.nativeEnum(Enums.DocumentArchiveListArchiveType),
  processing_status: z.nativeEnum(Enums.DocumentArchiveListProcessingStatus),
  processed_at: z.iso.datetime().nullable(),
  total_items: z.int(),
  total_chunks: z.int(),
  total_cost_usd: z.number(),
  processing_progress: z.number(),
  created_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DocumentArchiveList = z.infer<typeof DocumentArchiveListSchema>