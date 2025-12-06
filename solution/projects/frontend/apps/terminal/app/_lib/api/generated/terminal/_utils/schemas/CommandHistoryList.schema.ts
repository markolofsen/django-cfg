/**
 * Zod schema for CommandHistoryList
 *
 * This schema provides runtime validation and type inference.
 *  * Lightweight serializer for command lists.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Lightweight serializer for command lists.
 */
export const CommandHistoryListSchema = z.object({
  id: z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i),
  session_id: z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i),
  command: z.string(),
  status: z.nativeEnum(Enums.CommandHistoryListStatus).optional(),
  exit_code: z.int().min(-2147483648.0).max(2147483647.0).nullable().optional(),
  output_preview: z.string(),
  duration_ms: z.int(),
  is_success: z.boolean(),
  created_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CommandHistoryList = z.infer<typeof CommandHistoryListSchema>