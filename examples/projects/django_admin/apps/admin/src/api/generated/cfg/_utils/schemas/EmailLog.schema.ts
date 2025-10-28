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
  id: z.uuid(),
  user: z.int().nullable(),
  user_email: z.string(),
  newsletter: z.int().nullable(),
  newsletter_title: z.string(),
  recipient: z.string(),
  subject: z.string(),
  body: z.string(),
  status: z.nativeEnum(Enums.EmailLogStatus),
  created_at: z.iso.datetime(),
  sent_at: z.iso.datetime().nullable(),
  error_message: z.string().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type EmailLog = z.infer<typeof EmailLogSchema>