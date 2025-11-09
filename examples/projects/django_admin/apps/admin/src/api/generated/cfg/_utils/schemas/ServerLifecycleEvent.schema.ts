/**
 * Zod schema for ServerLifecycleEvent
 *
 * This schema provides runtime validation and type inference.
 *  * Server lifecycle event.
 *  */
import { z } from 'zod'

/**
 * Server lifecycle event.
 */
export const ServerLifecycleEventSchema = z.object({
  timestamp: z.string(),
  event_type: z.string(),
  server_address: z.string(),
  server_pid: z.int(),
  uptime_seconds: z.int().nullable().optional(),
  error_message: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServerLifecycleEvent = z.infer<typeof ServerLifecycleEventSchema>