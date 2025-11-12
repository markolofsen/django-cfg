/**
 * Zod schema for AppStatisticsData
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for application statistics data.
 *  */
import { z } from 'zod'
import { ModelStatisticsSchema } from './ModelStatistics.schema'

/**
 * Serializer for application statistics data.
 */
export const AppStatisticsDataSchema = z.object({
  name: z.string(),
  models: z.array(ModelStatisticsSchema),
  total_records: z.int(),
  model_count: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type AppStatisticsData = z.infer<typeof AppStatisticsDataSchema>