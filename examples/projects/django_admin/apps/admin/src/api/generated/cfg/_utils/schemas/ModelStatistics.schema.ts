/**
 * Zod schema for ModelStatistics
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for individual model statistics.
 *  */
import { z } from 'zod'

/**
 * Serializer for individual model statistics.
 */
export const ModelStatisticsSchema = z.object({
  model_name: z.string(),
  name: z.string(),
  count: z.int(),
  fields_count: z.int(),
  admin_url: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ModelStatistics = z.infer<typeof ModelStatisticsSchema>