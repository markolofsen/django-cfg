/**
 * Zod schema for PatchedChatResponseRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Chat response serializer.
 *  */
import { z } from 'zod'
import { ChatSourceRequestSchema } from './ChatSourceRequest.schema'

/**
 * Chat response serializer.
 */
export const PatchedChatResponseRequestSchema = z.object({
  message_id: z.uuid().optional(),
  content: z.string().min(1).optional(),
  tokens_used: z.int().optional(),
  cost_usd: z.number().optional(),
  processing_time_ms: z.int().optional(),
  model_used: z.string().min(1).optional(),
  sources: z.array(ChatSourceRequestSchema).nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedChatResponseRequest = z.infer<typeof PatchedChatResponseRequestSchema>