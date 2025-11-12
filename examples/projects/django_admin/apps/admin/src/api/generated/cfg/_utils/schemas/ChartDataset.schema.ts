/**
 * Zod schema for ChartDataset
 *
 * This schema provides runtime validation and type inference.
 *  * Chart.js dataset serializer.
 *  */
import { z } from 'zod'

/**
 * Chart.js dataset serializer.
 */
export const ChartDatasetSchema = z.object({
  label: z.string(),
  data: z.array(z.int()),
  backgroundColor: z.string(),
  borderColor: z.string(),
  tension: z.number(),
  fill: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChartDataset = z.infer<typeof ChartDatasetSchema>