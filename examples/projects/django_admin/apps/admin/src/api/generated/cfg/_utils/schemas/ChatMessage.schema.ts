/**
 * Zod schema for ChatMessage
 *
 * This schema provides runtime validation and type inference.
 *  * Chat message response serializer.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Chat message response serializer.
 */
export const ChatMessageSchema = z.object({
  id: z.uuid(),
  role: z.nativeEnum(Enums.ChatMessageRole),
  content: z.string(),
  tokens_used: z.int().min(0.0).max(2147483647.0).optional(),
  cost_usd: z.number(),
  processing_time_ms: z.int().min(0.0).max(2147483647.0).optional(),
  created_at: z.iso.datetime(),
  context_chunks: z.record(z.string(), z.any()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChatMessage = z.infer<typeof ChatMessageSchema>