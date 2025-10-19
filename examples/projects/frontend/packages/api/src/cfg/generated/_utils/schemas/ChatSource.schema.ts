/**
 * Zod schema for ChatSource
 *
 * This schema provides runtime validation and type inference.
 *  * Chat source document information serializer.
 *  */
import { z } from 'zod'

/**
 * Chat source document information serializer.
 */
export const ChatSourceSchema = z.object({
  document_title: z.string(),
  chunk_content: z.string(),
  similarity: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChatSource = z.infer<typeof ChatSourceSchema>