/**
 * Zod schema for ChatSession
 *
 * This schema provides runtime validation and type inference.
 *  * Chat session response serializer.
 *  */
import { z } from 'zod'

/**
 * Chat session response serializer.
 */
export const ChatSessionSchema = z.object({
  id: z.uuid(),
  title: z.string().max(255).optional(),
  is_active: z.boolean().optional(),
  messages_count: z.int().min(0.0).max(2147483647.0).optional(),
  total_tokens_used: z.int().min(0.0).max(2147483647.0).optional(),
  total_cost_usd: z.number(),
  model_name: z.string().max(100).optional(),
  temperature: z.number().optional(),
  max_context_chunks: z.int().min(0.0).max(2147483647.0).optional(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChatSession = z.infer<typeof ChatSessionSchema>