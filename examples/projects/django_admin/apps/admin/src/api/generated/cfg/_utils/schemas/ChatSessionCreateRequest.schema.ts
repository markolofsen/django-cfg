/**
 * Zod schema for ChatSessionCreateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Chat session creation request serializer.
 *  */
import { z } from 'zod'

/**
 * Chat session creation request serializer.
 */
export const ChatSessionCreateRequestSchema = z.object({
  title: z.string().max(255).optional(),
  model_name: z.string().min(1).max(100).optional(),
  temperature: z.number().min(0.0).max(2.0).optional(),
  max_context_chunks: z.int().min(1.0).max(10.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChatSessionCreateRequest = z.infer<typeof ChatSessionCreateRequestSchema>