/**
 * Zod schema for ArchiveItem
 *
 * This schema provides runtime validation and type inference.
 *  * Archive item serializer.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Archive item serializer.
 */
export const ArchiveItemSchema = z.object({
  id: z.uuid(),
  relative_path: z.string().max(1024),
  item_name: z.string().max(255),
  item_type: z.string().max(100),
  content_type: z.nativeEnum(Enums.ArchiveItemContentType),
  file_size: z.int().min(0.0).max(2147483647.0).optional(),
  is_processable: z.boolean(),
  language: z.string(),
  encoding: z.string(),
  chunks_count: z.int(),
  total_tokens: z.int(),
  processing_cost: z.number(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ArchiveItem = z.infer<typeof ArchiveItemSchema>