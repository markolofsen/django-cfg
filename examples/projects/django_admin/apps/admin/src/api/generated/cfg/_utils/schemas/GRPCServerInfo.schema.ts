/**
 * Zod schema for GRPCServerInfo
 *
 * This schema provides runtime validation and type inference.
 *  * Complete gRPC server information response.
 *  */
import { z } from 'zod'
import { GRPCInterceptorInfoSchema } from './GRPCInterceptorInfo.schema'
import { GRPCServiceInfoSchema } from './GRPCServiceInfo.schema'
import { GRPCStatsSchema } from './GRPCStats.schema'

/**
 * Complete gRPC server information response.
 */
export const GRPCServerInfoSchema = z.object({
  server_status: z.string(),
  address: z.string(),
  started_at: z.string().nullable().optional(),
  uptime_seconds: z.int().nullable().optional(),
  services: z.array(GRPCServiceInfoSchema).optional(),
  interceptors: z.array(GRPCInterceptorInfoSchema).optional(),
  stats: GRPCStatsSchema,
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCServerInfo = z.infer<typeof GRPCServerInfoSchema>