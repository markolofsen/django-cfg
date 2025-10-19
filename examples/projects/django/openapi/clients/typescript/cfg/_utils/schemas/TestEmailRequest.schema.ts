/**
 * Zod schema for TestEmailRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Simple serializer for test email.
 *  */
import { z } from 'zod'

/**
 * Simple serializer for test email.
 */
export const TestEmailRequestSchema = z.object({
  email: z.email(),
  subject: z.string().min(1).max(255).optional(),
  message: z.string().min(1).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TestEmailRequest = z.infer<typeof TestEmailRequestSchema>