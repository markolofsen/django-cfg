/**
 * Zod schema for GRPCFrameworkConfig
 *
 * This schema provides runtime validation and type inference.
 *  * gRPC framework configuration details.
 *  */
import { z } from 'zod'

/**
 * gRPC framework configuration details.
 */
export const GRPCFrameworkConfigSchema = z.object({
  enabled: z.boolean(),
  auto_discover: z.boolean(),
  services_path: z.string(),
  interceptors: z.array(z.string()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCFrameworkConfig = z.infer<typeof GRPCFrameworkConfigSchema>