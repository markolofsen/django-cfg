/**
 * Zod schema for HealthCheck
 *
 * This schema provides runtime validation and type inference.
 *  * Health check response.
 *  */
import { z } from 'zod'

/**
 * Health check response.
 */
export const HealthCheckSchema = z.object({
  status: z.string(),
  wrapper_url: z.string(),
  has_api_key: z.boolean(),
  timestamp: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type HealthCheck = z.infer<typeof HealthCheckSchema>