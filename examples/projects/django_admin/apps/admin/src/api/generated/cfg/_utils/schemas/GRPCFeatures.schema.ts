/**
 * Zod schema for GRPCFeatures
 *
 * This schema provides runtime validation and type inference.
 *  * gRPC features configuration.
 *  */
import { z } from 'zod'

/**
 * gRPC features configuration.
 */
export const GRPCFeaturesSchema = z.object({
  api_key_auth: z.boolean(),
  request_logging: z.boolean(),
  metrics: z.boolean(),
  reflection: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCFeatures = z.infer<typeof GRPCFeaturesSchema>