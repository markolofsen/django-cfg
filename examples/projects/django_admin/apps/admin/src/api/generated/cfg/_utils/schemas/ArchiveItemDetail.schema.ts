/**
 * Zod schema for ArchiveItemDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Detailed archive item serializer with content.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Detailed archive item serializer with content.
 */
export const ArchiveItemDetailSchema = z.object({
  id: z.uuid(),
  relative_path: z.string().max(1024),
  item_name: z.string().max(255),
  item_type: z.string().max(100),
  content_type: z.nativeEnum(Enums.ArchiveItemDetailContentType),
  file_size: z.int().min(0.0).max(2147483647.0).optional(),
  is_processable: z.boolean(),
  language: z.string(),
  encoding: z.string(),
  chunks_count: z.int(),
  total_tokens: z.int(),
  processing_cost: z.number(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
  raw_content: z.string(),
  metadata: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ArchiveItemDetail = z.infer<typeof ArchiveItemDetailSchema>