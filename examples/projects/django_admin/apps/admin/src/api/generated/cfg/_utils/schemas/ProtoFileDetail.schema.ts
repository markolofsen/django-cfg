/**
 * Zod schema for ProtoFileDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Proto file metadata.
 *  */
import { z } from 'zod'

/**
 * Proto file metadata.
 */
export const ProtoFileDetailSchema = z.object({
  app_label: z.string(),
  filename: z.string(),
  size_bytes: z.int(),
  package: z.string(),
  messages_count: z.int(),
  services_count: z.int(),
  created_at: z.number(),
  modified_at: z.number(),
  download_url: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ProtoFileDetail = z.infer<typeof ProtoFileDetailSchema>