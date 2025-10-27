/**
 * Zod schema for CentrifugoMetrics
 *
 * This schema provides runtime validation and type inference.
 *  * Server metrics.
 *  */
import { z } from 'zod'

/**
 * Server metrics.
 */
export const CentrifugoMetricsSchema = z.object({
  interval: z.number(),
  items: z.record(z.string(), z.any()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoMetrics = z.infer<typeof CentrifugoMetricsSchema>