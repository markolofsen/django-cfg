/**
 * Zod schema for GRPCHealthCheck
 *
 * This schema provides runtime validation and type inference.
 *  * gRPC health check response.
 *  */
import { z } from 'zod'

/**
 * gRPC health check response.
 */
export const GRPCHealthCheckSchema = z.object({
  status: z.string(),
  server_host: z.string(),
  server_port: z.int(),
  enabled: z.boolean(),
  timestamp: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCHealthCheck = z.infer<typeof GRPCHealthCheckSchema>