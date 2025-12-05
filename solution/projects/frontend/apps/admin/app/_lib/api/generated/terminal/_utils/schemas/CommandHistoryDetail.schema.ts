/**
 * Zod schema for CommandHistoryDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Full serializer for command details.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Full serializer for command details.
 */
export const CommandHistoryDetailSchema = z.object({
  id: z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i),
  session_id: z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i),
  session_name: z.string(),
  duration_ms: z.int(),
  is_success: z.boolean(),
  command: z.string(),
  working_directory: z.string().max(500).optional(),
  status: z.nativeEnum(Enums.CommandHistoryDetailStatus).optional(),
  stdout: z.string().optional(),
  stderr: z.string().optional(),
  exit_code: z.int().min(-2147483648.0).max(2147483647.0).nullable().optional(),
  started_at: z.iso.datetime().nullable().optional(),
  finished_at: z.iso.datetime().nullable().optional(),
  bytes_in: z.int().min(0.0).max(2147483647.0).optional(),
  bytes_out: z.int().min(0.0).max(2147483647.0).optional(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
  session: z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CommandHistoryDetail = z.infer<typeof CommandHistoryDetailSchema>