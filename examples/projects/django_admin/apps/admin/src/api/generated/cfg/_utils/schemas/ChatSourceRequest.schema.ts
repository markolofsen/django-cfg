/**
 * Zod schema for ChatSourceRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Chat source document information serializer.
 *  */
import { z } from 'zod'

/**
 * Chat source document information serializer.
 */
export const ChatSourceRequestSchema = z.object({
  document_title: z.string().min(1),
  chunk_content: z.string().min(1),
  similarity: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChatSourceRequest = z.infer<typeof ChatSourceRequestSchema>