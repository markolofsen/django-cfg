/**
 * Zod schema for PatchedChatSessionRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Chat session response serializer.
 *  */
import { z } from 'zod'

/**
 * Chat session response serializer.
 */
export const PatchedChatSessionRequestSchema = z.object({
  title: z.string().max(255).optional(),
  is_active: z.boolean().optional(),
  messages_count: z.int().min(0.0).max(2147483647.0).optional(),
  total_tokens_used: z.int().min(0.0).max(2147483647.0).optional(),
  model_name: z.string().min(1).max(100).optional(),
  temperature: z.number().optional(),
  max_context_chunks: z.int().min(0.0).max(2147483647.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedChatSessionRequest = z.infer<typeof PatchedChatSessionRequestSchema>