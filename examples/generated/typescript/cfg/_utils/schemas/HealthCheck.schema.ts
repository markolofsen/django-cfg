/**
 * Zod schema for HealthCheck
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for health check response.
 *  */
import { z } from 'zod'

/**
 * Serializer for health check response.
 */
export const HealthCheckSchema = z.object({
  status: z.string(),
  timestamp: z.string().datetime(),
  service: z.string(),
  version: z.string(),
  checks: z.record(z.string(), z.any()),
  environment: z.record(z.string(), z.any()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type HealthCheck = z.infer<typeof HealthCheckSchema>