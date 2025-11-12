/**
 * Zod schema for BulkEmailRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Simple serializer for bulk email.
 *  */
import { z } from 'zod'

/**
 * Simple serializer for bulk email.
 */
export const BulkEmailRequestSchema = z.object({
  recipients: z.array(z.email()),
  subject: z.string().min(1).max(255),
  email_title: z.string().min(1).max(255),
  main_text: z.string().min(1),
  main_html_content: z.string().optional(),
  button_text: z.string().max(100).optional(),
  button_url: z.url().optional(),
  secondary_text: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type BulkEmailRequest = z.infer<typeof BulkEmailRequestSchema>