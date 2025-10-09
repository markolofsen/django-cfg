/**
 * Zod schema for EmailLog
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for EmailLog model.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for EmailLog model.
 */
export const EmailLogSchema = z.object({
  id: z.string().uuid(),
  user: z.number().int().optional(),
  user_email: z.string(),
  newsletter: z.number().int().optional(),
  newsletter_title: z.string(),
  recipient: z.string(),
  subject: z.string(),
  body: z.string(),
  status: z.nativeEnum(Enums.EmailLogStatus),
  created_at: z.string().datetime(),
  sent_at: z.string().datetime().optional(),
  error_message: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type EmailLog = z.infer<typeof EmailLogSchema>