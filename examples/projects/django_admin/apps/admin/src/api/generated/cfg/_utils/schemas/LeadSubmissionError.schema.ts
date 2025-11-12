/**
 * Zod schema for LeadSubmissionError
 *
 * This schema provides runtime validation and type inference.
 *  * Response serializer for lead submission errors.
 *  */
import { z } from 'zod'

/**
 * Response serializer for lead submission errors.
 */
export const LeadSubmissionErrorSchema = z.object({
  success: z.boolean(),
  error: z.string(),
  details: z.record(z.string(), z.record(z.string(), z.any())).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type LeadSubmissionError = z.infer<typeof LeadSubmissionErrorSchema>