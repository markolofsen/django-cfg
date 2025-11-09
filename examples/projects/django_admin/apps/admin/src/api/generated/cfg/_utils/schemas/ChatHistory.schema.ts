/**
 * Zod schema for ChatHistory
 *
 * This schema provides runtime validation and type inference.
 *  * Chat history response serializer.
 *  */
import { z } from 'zod'
import { ChatMessageSchema } from './ChatMessage.schema'

/**
 * Chat history response serializer.
 */
export const ChatHistorySchema = z.object({
  session_id: z.uuid(),
  messages: z.array(ChatMessageSchema),
  total_messages: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChatHistory = z.infer<typeof ChatHistorySchema>