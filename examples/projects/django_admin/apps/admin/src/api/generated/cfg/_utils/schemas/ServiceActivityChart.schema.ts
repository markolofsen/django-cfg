/**
 * Zod schema for ServiceActivityChart
 *
 * This schema provides runtime validation and type inference.
 *  * Service activity comparison chart data.
 *  */
import { z } from 'zod'
import { ServiceActivityDataPointSchema } from './ServiceActivityDataPoint.schema'

/**
 * Service activity comparison chart data.
 */
export const ServiceActivityChartSchema = z.object({
  title: z.string().optional(),
  services: z.array(ServiceActivityDataPointSchema).optional(),
  period_hours: z.int(),
  total_services: z.int(),
  most_active_service: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServiceActivityChart = z.infer<typeof ServiceActivityChartSchema>