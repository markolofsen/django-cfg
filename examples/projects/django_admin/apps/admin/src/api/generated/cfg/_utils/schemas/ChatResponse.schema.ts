/**
 * Zod schema for ChatResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Chat response serializer.
 *  */
import { z } from 'zod'
import { ChatSourceSchema } from './ChatSource.schema'

/**
 * Chat response serializer.
 */
export const ChatResponseSchema = z.object({
  message_id: z.uuid(),
  content: z.string(),
  tokens_used: z.int(),
  cost_usd: z.number(),
  processing_time_ms: z.int(),
  model_used: z.string(),
  sources: z.array(ChatSourceSchema).nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChatResponse = z.infer<typeof ChatResponseSchema>