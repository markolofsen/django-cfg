/**
 * Zod schema for Message
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { SenderSchema } from './Sender.schema'

export const MessageSchema = z.object({
  uuid: z.string().uuid(),
  ticket: z.string().uuid(),
  sender: SenderSchema,
  is_from_author: z.boolean(),
  text: z.string(),
  created_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Message = z.infer<typeof MessageSchema>