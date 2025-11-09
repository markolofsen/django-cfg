/**
 * Zod schema for GRPCServerConfig
 *
 * This schema provides runtime validation and type inference.
 *  * gRPC server configuration details.
 *  */
import { z } from 'zod'

/**
 * gRPC server configuration details.
 */
export const GRPCServerConfigSchema = z.object({
  host: z.string(),
  port: z.int(),
  enabled: z.boolean(),
  max_concurrent_streams: z.int().nullable().optional(),
  max_concurrent_rpcs: z.int().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCServerConfig = z.infer<typeof GRPCServerConfigSchema>