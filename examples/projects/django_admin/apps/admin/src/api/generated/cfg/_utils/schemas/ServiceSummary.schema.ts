/**
 * Zod schema for ServiceSummary
 *
 * This schema provides runtime validation and type inference.
 *  * Summary information for a single service.
 *  */
import { z } from 'zod'

/**
 * Summary information for a single service.
 */
export const ServiceSummarySchema = z.object({
  name: z.string(),
  full_name: z.string(),
  package: z.string(),
  methods_count: z.int(),
  total_requests: z.int().optional(),
  success_rate: z.number().optional(),
  avg_duration_ms: z.number().optional(),
  last_activity_at: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServiceSummary = z.infer<typeof ServiceSummarySchema>