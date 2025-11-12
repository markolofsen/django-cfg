/**
 * Zod schema for MessageCreate
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'

export const MessageCreateSchema = z.object({
  text: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type MessageCreate = z.infer<typeof MessageCreateSchema>