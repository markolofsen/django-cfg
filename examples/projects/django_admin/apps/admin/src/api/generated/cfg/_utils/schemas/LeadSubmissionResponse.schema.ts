/**
 * Zod schema for LeadSubmissionResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response serializer for successful lead submission.
 *  */
import { z } from 'zod'

/**
 * Response serializer for successful lead submission.
 */
export const LeadSubmissionResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  lead_id: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type LeadSubmissionResponse = z.infer<typeof LeadSubmissionResponseSchema>