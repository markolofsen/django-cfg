/**
 * Zod schema for SystemMetrics
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for system performance metrics.
 *  */
import { z } from 'zod'

/**
 * Serializer for system performance metrics.
 */
export const SystemMetricsSchema = z.object({
  cpu_usage: z.number(),
  memory_usage: z.number(),
  disk_usage: z.number(),
  network_in: z.string(),
  network_out: z.string(),
  response_time: z.string(),
  uptime: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SystemMetrics = z.infer<typeof SystemMetricsSchema>