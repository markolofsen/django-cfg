/**
 * Zod schema for GRPCServerStatus
 *
 * This schema provides runtime validation and type inference.
 *  * gRPC server status and information for overview stats.
 *  */
import { z } from 'zod'
import { GRPCRegisteredServiceSchema } from './GRPCRegisteredService.schema'

/**
 * gRPC server status and information for overview stats.
 */
export const GRPCServerStatusSchema = z.object({
  status: z.string(),
  is_running: z.boolean(),
  host: z.string(),
  port: z.int(),
  address: z.string(),
  pid: z.int().nullable(),
  started_at: z.iso.datetime().nullable(),
  uptime_seconds: z.int(),
  uptime_display: z.string(),
  registered_services_count: z.int(),
  enable_reflection: z.boolean(),
  enable_health_check: z.boolean(),
  last_heartbeat: z.iso.datetime().nullable(),
  services: z.array(GRPCRegisteredServiceSchema),
  services_healthy: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCServerStatus = z.infer<typeof GRPCServerStatusSchema>