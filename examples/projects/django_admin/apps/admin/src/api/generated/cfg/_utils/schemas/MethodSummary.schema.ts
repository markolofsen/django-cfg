/**
 * Zod schema for MethodSummary
 *
 * This schema provides runtime validation and type inference.
 *  * Summary information for a method.
 *  */
import { z } from 'zod'
import { MethodStatsSchema } from './MethodStats.schema'

/**
 * Summary information for a method.
 */
export const MethodSummarySchema = z.object({
  name: z.string(),
  full_name: z.string(),
  service_name: z.string(),
  request_type: z.string().optional(),
  response_type: z.string().optional(),
  stats: MethodStatsSchema,
})

/**
 * Infer TypeScript type from Zod schema
 */
export type MethodSummary = z.infer<typeof MethodSummarySchema>