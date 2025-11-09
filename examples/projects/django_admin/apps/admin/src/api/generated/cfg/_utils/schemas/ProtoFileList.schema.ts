/**
 * Zod schema for ProtoFileList
 *
 * This schema provides runtime validation and type inference.
 *  * List of proto files.
 *  */
import { z } from 'zod'
import { ProtoFileDetailSchema } from './ProtoFileDetail.schema'

/**
 * List of proto files.
 */
export const ProtoFileListSchema = z.object({
  files: z.array(ProtoFileDetailSchema),
  total_files: z.int(),
  proto_dir: z.string(),
  download_all_url: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ProtoFileList = z.infer<typeof ProtoFileListSchema>