/**
 * Zod schema for ChatQueryRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Chat query request serializer.
 *  */
import { z } from 'zod'

/**
 * Chat query request serializer.
 */
export const ChatQueryRequestSchema = z.object({
  session_id: z.uuid().nullable().optional(),
  query: z.string().min(1).max(2000),
  max_tokens: z.int().min(1.0).max(4000.0).optional(),
  include_sources: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChatQueryRequest = z.infer<typeof ChatQueryRequestSchema>