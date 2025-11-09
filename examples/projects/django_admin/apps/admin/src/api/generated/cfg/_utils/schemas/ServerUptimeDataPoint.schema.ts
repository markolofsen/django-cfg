/**
 * Zod schema for ServerUptimeDataPoint
 *
 * This schema provides runtime validation and type inference.
 *  * Server uptime data point.
 *  */
import { z } from 'zod'

/**
 * Server uptime data point.
 */
export const ServerUptimeDataPointSchema = z.object({
  timestamp: z.string(),
  server_count: z.int(),
  servers: z.array(z.string()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServerUptimeDataPoint = z.infer<typeof ServerUptimeDataPointSchema>