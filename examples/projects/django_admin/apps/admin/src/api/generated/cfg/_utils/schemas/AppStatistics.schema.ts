/**
 * Zod schema for AppStatistics
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for application-specific statistics.
 *  */
import { z } from 'zod'
import { AppStatisticsDataSchema } from './AppStatisticsData.schema'

/**
 * Serializer for application-specific statistics.
 */
export const AppStatisticsSchema = z.object({
  app_name: z.string(),
  statistics: AppStatisticsDataSchema,
})

/**
 * Infer TypeScript type from Zod schema
 */
export type AppStatistics = z.infer<typeof AppStatisticsSchema>