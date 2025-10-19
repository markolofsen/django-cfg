/**
 * Zod schema for MessageCreateRequest
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'

export const MessageCreateRequestSchema = z.object({
  text: z.string().min(1),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type MessageCreateRequest = z.infer<typeof MessageCreateRequestSchema>