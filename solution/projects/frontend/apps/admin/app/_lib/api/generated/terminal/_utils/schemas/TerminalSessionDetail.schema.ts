/**
 * Zod schema for TerminalSessionDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Full serializer for session details.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { CommandHistoryListSchema } from './CommandHistoryList.schema'

/**
 * Full serializer for session details.
 */
export const TerminalSessionDetailSchema = z.object({
  id: z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i),
  is_alive: z.boolean(),
  is_active: z.boolean(),
  display_name: z.string(),
  heartbeat_age_seconds: z.number(),
  recent_commands: z.array(CommandHistoryListSchema),
  name: z.string().max(100).optional(),
  status: z.nativeEnum(Enums.TerminalSessionDetailStatus),
  electron_hostname: z.string(),
  electron_version: z.string(),
  working_directory: z.string().max(500).optional(),
  shell: z.string().max(100).optional(),
  environment: z.record(z.string(), z.any()).optional(),
  commands_count: z.int(),
  bytes_sent: z.int(),
  bytes_received: z.int(),
  connected_at: z.iso.datetime().nullable(),
  last_heartbeat_at: z.iso.datetime().nullable(),
  disconnected_at: z.iso.datetime().nullable(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
  user: z.int().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TerminalSessionDetail = z.infer<typeof TerminalSessionDetailSchema>