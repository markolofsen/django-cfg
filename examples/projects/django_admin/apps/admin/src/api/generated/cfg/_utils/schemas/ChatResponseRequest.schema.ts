/**
 * Zod schema for ChatResponseRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Chat response serializer.
 *  */
import { z } from 'zod'
import { ChatSourceRequestSchema } from './ChatSourceRequest.schema'

/**
 * Chat response serializer.
 */
export const ChatResponseRequestSchema = z.object({
  message_id: z.uuid(),
  content: z.string().min(1),
  tokens_used: z.int(),
  cost_usd: z.number(),
  processing_time_ms: z.int(),
  model_used: z.string().min(1),
  sources: z.array(ChatSourceRequestSchema).nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChatResponseRequest = z.infer<typeof ChatResponseRequestSchema>