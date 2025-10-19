/**
 * Zod schema for MessageRequest
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'

export const MessageRequestSchema = z.object({
  text: z.string().min(1),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type MessageRequest = z.infer<typeof MessageRequestSchema>