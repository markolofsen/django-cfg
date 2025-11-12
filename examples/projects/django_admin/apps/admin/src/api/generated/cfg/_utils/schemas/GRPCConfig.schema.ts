/**
 * Zod schema for GRPCConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Complete gRPC configuration response.
 *  */
import { z } from 'zod'
import { GRPCFeaturesSchema } from './GRPCFeatures.schema'
import { GRPCFrameworkConfigSchema } from './GRPCFrameworkConfig.schema'
import { GRPCServerConfigSchema } from './GRPCServerConfig.schema'

/**
 * Complete gRPC configuration response.
 */
export const GRPCConfigSchema = z.object({
  server: GRPCServerConfigSchema,
  framework: GRPCFrameworkConfigSchema,
  features: GRPCFeaturesSchema,
  registered_services: z.int(),
  total_methods: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCConfig = z.infer<typeof GRPCConfigSchema>