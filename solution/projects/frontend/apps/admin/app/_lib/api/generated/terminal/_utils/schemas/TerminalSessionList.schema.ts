/**
 * Zod schema for TerminalSessionList
 *
 * This schema provides runtime validation and type inference.
 *  * Lightweight serializer for session lists.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Lightweight serializer for session lists.
 */
export const TerminalSessionListSchema = z.object({
  id: z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i),
  name: z.string().max(100).optional(),
  status: z.nativeEnum(Enums.TerminalSessionListStatus).optional(),
  display_name: z.string(),
  is_alive: z.boolean(),
  electron_hostname: z.string().max(255).optional(),
  working_directory: z.string().max(500).optional(),
  shell: z.string().max(100).optional(),
  connected_at: z.iso.datetime().nullable().optional(),
  last_heartbeat_at: z.iso.datetime().nullable().optional(),
  created_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TerminalSessionList = z.infer<typeof TerminalSessionListSchema>