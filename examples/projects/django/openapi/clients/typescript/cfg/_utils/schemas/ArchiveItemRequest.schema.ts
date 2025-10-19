/**
 * Zod schema for ArchiveItemRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Archive item serializer.
 *  */
import { z } from 'zod'

/**
 * Archive item serializer.
 */
export const ArchiveItemRequestSchema = z.object({
  relative_path: z.string().min(1).max(1024),
  item_name: z.string().min(1).max(255),
  item_type: z.string().min(1).max(100),
  file_size: z.int().min(0.0).max(2147483647.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ArchiveItemRequest = z.infer<typeof ArchiveItemRequestSchema>