/**
 * Zod schema for BulkEmailResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response for bulk email sending.
 *  */
import { z } from 'zod'

/**
 * Response for bulk email sending.
 */
export const BulkEmailResponseSchema = z.object({
  success: z.boolean(),
  sent_count: z.int(),
  failed_count: z.int(),
  total_recipients: z.int(),
  error: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type BulkEmailResponse = z.infer<typeof BulkEmailResponseSchema>