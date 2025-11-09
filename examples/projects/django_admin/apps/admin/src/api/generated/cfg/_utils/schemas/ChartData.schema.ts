/**
 * Zod schema for ChartData
 *
 * This schema provides runtime validation and type inference.
 *  * Chart.js data structure serializer.
 *  */
import { z } from 'zod'
import { ChartDatasetSchema } from './ChartDataset.schema'

/**
 * Chart.js data structure serializer.
 */
export const ChartDataSchema = z.object({
  labels: z.array(z.string()),
  datasets: z.array(ChartDatasetSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChartData = z.infer<typeof ChartDataSchema>